
#startup
import math



import pygame
import math

from direct.showbase.PythonUtil import appendStr
from direct.showutil.BuildGeometry import circleX
from keyboard import key_to_scan_codes

pygame.mixer.init()
sound1 = pygame.mixer.Sound("High Whoosh.wav")
b1 = pygame.mixer.Sound("Basketball Bounce.wav")
b2 = pygame.mixer.Sound("Basketball Bounce2.wav")
b3 = pygame.mixer.Sound("Basketball Bounce4.wav")
b4 = pygame.mixer.Sound("Basketball Bounce5.wav")
sound3 = pygame.mixer.Sound("Kick Drum (1).wav")
s1 = pygame.mixer.Sound("slide (1).wav")
r = pygame.mixer.Sound("Low Whoosh.wav")
bgm1 = pygame.mixer.Sound("04.wav")
up = pygame.mixer.Sound("unpau.wav")
p = pygame.mixer.Sound("pau.wav")
# Play each sound on a separate channel


pygame.mixer.set_num_channels(100)  # must be > 10 if you use Channel(10)

pygame.mixer.Channel(0).play(sound1)



import keyboard
from ursina import *
from ursina import held_keys, mouse
from ursina import time
# Initialize Pygame
pygame.init()
pygame.joystick.init()

# Detect controllers
joystick_count = pygame.joystick.get_count()
if joystick_count == 0:
    print("No controller detected!")

# Open first controller
joystick = pygame.joystick.Joystick(0)
joystick.init()
print(f"Using controller: {joystick.get_name()}")

# Variables for sticks
lstick_x = 0.0
lstick_y = 0.0
rstick_x = 0.0
rstick_y = 0.0

clock = pygame.time.Clock()

import random
pygame.display.set_caption("Stormblade adventures")

app = Ursina()

# Load the color-limited shader

lol = 3
speed_y= 0
playery=0
speedx=0
speedz=0
playerx=0
playerz=0
decellx=0
decellz=0
camx=0
camy=0
camz=0
dx=0
dy=0
dz=0
bx=0
by=10
bz=0
bsx=0
bsy=0
bsz=0
frame=0
speed=0
gb=1
gbt=0
bdx=0
bdy=0
bdz=0
press=0
cox=0
coz=0
utg=0
xx=0
zz=0
debug=1
whaid=0
camyy=40
speedxxxx=0
spex=0
result = 0
s ='s'
framelast = 0
sframe = 5
dir=9
e = 0
roll=0
sirol=0
drol=0
slide = 0
tree_frame = 0
tree_sprite = 0
TICK =0
editor =1
xxx = 0
yyy = 0
zzz = 0
pressed =0
landed = 0
spin = 0
sf = 0
lpress = 0
llpress = 0
yy = 0
dyy = 0
anim = 0
colx =0
coly =0
colz = 0
walljump=0
sy =0
s45 =0
impact = 0
impact_last = 0
wallrunx = 0
wallrunz = 0
walz = 0
walx = 0
yyyy = 0
w = 0
bcaw = 0
wap = 0
ss = 0
bcas = 0
sap = 0
gager = 0
yaye = 0
gagle = 0
dir_y = -55
zoom = 0
rots=0
aii = 0
re = 0
re2 = 0
type = 0
stop = 0
ini = 1
ex = 0
ey = 0
ez = 0
esy = 0
esz = 0
esx = 0
eh = 0
bgm2 = pygame.mixer.Sound("39 .wav")
#pygame.mixer.Channel(17).play(bgm2)

if keyboard.is_pressed("space"):
    if speed_y < 0:
        if speedz > 0.05:
            wallrunz = 10

def controls():
    global speed_y
    global playery
    global speedx
    global speedz
    global playerx
    global playerz
    global decellx
    global decellz
    global camx
    global camy
    global camz
    global dx
    global dy
    global dz
    global bx
    global by
    global bz
    global bsx
    global bsy
    global bsz
    global frame
    global dir
    global speed
    global gb
    global gbt
    global bdx
    global bdy
    global bsz
    global frame
    global dir
    global speed
    global press
    global cox
    global coz
    global utg
    global xx
    global zz
    global debug
    global whaid
    global camyy
    global spex
    global speedxxxx
    global result
    global framelast
    global sframe
    global s
    global e
    global roll
    global isrol
    global drol
    global slide
    global tree_frame
    global tree_sprite
    global TICK
    global editor
    global xxx
    global zzz
    global yyy
    global sirol
    global landed
    global pressed
    global spin
    global sf
    global lpress
    global llpress
    global yy
    global dyy
    global anim
    global colx
    global coly
    global colz
    global walljump
    global sy
    global s45
    global impact
    global impact_last
    global block_info
    global wallrunz
    global wallrunx
    global walz
    global walx
    global yyyy
    global bcaw
    global w
    global wap
    global bcas
    global sap
    global ss
    global gager
    global yaye
    global gagle
    global dir_y
    global rots
    global zoom
    global aii
    global re
    global re2
    global type
    global pause
    global pi
    global dob_tim
    global stop
    global ap
    global slow
    global slowp
    global light1
    global lstick_y
    global lstick_x
    global rstick_x
    global rstick_y
    global y_text_intro
    global ini
    global gags

    if playery < -1.5:
        walljump = 0
        lpress = 0
        utg = 1
        playery = -1.5
        speed_y = 0
        decellx = 0.8
        decellz = 0.8
        speed_y = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Handle analog stick movement
        if event.type == pygame.JOYAXISMOTION:
            if event.axis == 0:  # Left stick X-axis
                lstick_x = event.value
            elif event.axis == 1:  # Left stick Y-axis
                lstick_y = event.value
            elif event.axis == 3:  # Right stick X-axis (commonly axis 3)
                rstick_x = event.value
            elif event.axis == 4:  # Right stick Y-axis (commonly axis 4)
                rstick_y = event.value


    if impact_last < 0:
        if speed_y < 0 :
           if not speed_y == 0 :
               if slow == -1:
                   speed_y -= 10 * time.dt / 2
               else:
                   speed_y -= 10 * time.dt
        else :
            if slow == -1:
                speed_y -= 7 * time.dt / 2
            else:
                speed_y -= 7 * time.dt
    if debug ==1:
     if impact_last < 0:

      if slide == 0 :
        if keyboard.is_pressed('w') or lstick_y < 0:
            if wallrunx < 0:
                if slow == -1:
                    speedx += math.sin(math.radians(dir_y + 0)) * -0.0075 * 0.5
                    speedz += math.cos(math.radians(dir_y + 0)) * 0.0075 * 0.5
                else:
                    speedx += math.sin(math.radians(dir_y + 0)) * -0.0075
                    speedz += math.cos(math.radians(dir_y + 0)) * 0.0075
            decellx = 0.99
            decellz = 0.99
        frame += speed/40
        if keyboard.is_pressed('s') or lstick_y > 0:
            if wallrunx < 0:
                if slow == -1:
                    speedx += math.sin(math.radians(dir_y + 180)) * -0.0075 * 0.5
                    speedz += math.cos(math.radians(dir_y + 180)) * 0.0075 * 0.5
                else:
                    speedx += math.sin(math.radians(dir_y + 180)) * -0.0075
                    speedz += math.cos(math.radians(dir_y + 180)) * 0.0075
                decellx = 0.99
                decellz = 0.99
        frame += speed/40
        if keyboard.is_pressed('d') or lstick_x > 0:
            if wallrunz < 0:
                if slow == -1:
                    speedx += math.sin(math.radians(dir_y + -90)) * -0.0075 * 0.5
                    speedz += math.cos(math.radians(dir_y + -90)) * 0.0075 * 0.5
                else:
                    speedx += math.sin(math.radians(dir_y + -90)) * -0.0075
                    speedz += math.cos(math.radians(dir_y + -90)) * 0.0075
                decellx = 0.99
                decellz = 0.99
        frame += speed/40
        if keyboard.is_pressed('a') or lstick_x < 0:
            if wallrunz < 0:
                if slow == -1:
                    speedx += math.sin(math.radians(dir_y + 90)) * -0.0075 * 0.5
                    speedz += math.cos(math.radians(dir_y + 90)) * 0.0075 * 0.5
                else:
                    speedx += math.sin(math.radians(dir_y + 90)) * -0.0075
                    speedz += math.cos(math.radians(dir_y + 90)) * 0.0075
                decellx = 0.99
                decellz = 0.99
        frame += speed/40
        if keyboard.is_pressed('space') or joystick.get_button(0) == 1:
          if playery <-0.9:
              if slow == -1 :
                speed_y = 2.5 / 1.5 + speed * 6 / 3
              else:
                  speed_y = 2.5 / 1.5 + speed * 6
        if mouse.left == 1 and mouse.right == 1 or joystick.get_button(7) == 1 and  joystick.get_button(6) == 1:
            decellx = 0.7
            decellz = 0.7
        speedx = speedx * decellx
        speedz = speedz * decellz
        playerz += speedz * time.dt * 50
        playerx += speedx * time.dt * 50

      else:
         playerx += speedx
         playerz += speedz


    if not mouse.velocity[0] == 0 :
        dir_y += mouse.velocity[0] * -75

    if keyboard.is_pressed('right') or rstick_x > 0:
            dir_y += 3
    else:
        if keyboard.is_pressed('left') or rstick_x < 0:
                dir_y -= 3
        else:
            rots = 0
    if keyboard.is_pressed('down') or rstick_y > 0:
        zoom += 0.5
    if keyboard.is_pressed('up') or rstick_y < 0:
        zoom -= 0.5
    if rots > 3:
        rots = 3
    if rots < -3:
        rots = -3
    if zoom < 0 :
        zoom =0
    if zoom > 60:
        zoom =60
    dir_y += re

    gagle -= 1
    if bcas > -20 and 0 > bcas:
        if keyboard.is_pressed('space'):
            speed_y = 5 / 1.5 + speed * 3
            bcas = -20
    if walljump == 1 :
        if yaye == 0 :
            yaye = 1
            gagle = 2
    else:
        yaye = 0

    bcas -= 1
    ss -= 1
    if bcas == 0:
            drol = 1

    if bcas > 0:
            bcaw = 0
            cox = math.cos(math.radians(dir)) * 0.3
            coz = math.sin(math.radians(dir)) * 0.3
            speedz = coz
            speedx = cox
            playerz += speedz
            playerx += speedx
            speed_y = 0



    bcaw -= 1
    w -= 1


    yyyy += speed_y - yyyy * 0.5
    if yyyy < 0 :
        yyyy *= -1
    wallrunz-=1
    wallrunx-=1

    if wallrunz > 0:
        if walz ==1 :
            speed_y = -0.6
            speedx = 0
            speedz = 0.15
        if walz ==0 :
            speed_y = -0.6
            speedx = 0
            speedz = -0.15

    if wallrunx > 0:
        if walx ==0:
            speed_y = -0.6
            speedx = -0.15
            speedz = 0
        if walx ==1:
            speed_y = -0.6
            speedx = 0.15
            speedz = 0

    if keyboard.press("shift"):
        if speed_y < 0 :
            if impact_last < 0:
                speed_y -=1


DirectionalLight(shadows=True, y=10, z=10, rotation=(45, -45, 45))
AmbientLight(color=color.rgba(100, 100, 100, 0.5))

#def scripts
def coli():
    global playerx,playerz,playery,speedx,speedz,speed_y,colx,coly,colz,walljump,impact_last,impact,walz,wallrunz,walx,wallrunx,bcaw,gager,type,decellz,decellx,speed_y
    if playerx > -1.5 + colx:
        if playerx < 1.5 + colx:
            if playery > -1.5 - 1.5 + coly:
                if playery < 1.3 - 1.5 + coly:
                    if playerz < -1+ colz:
                        if playerz > -1.5+colz:

                          if type == 1 or type == 2:

                            playerz = -1.5+colz
                            speedz *= 0
                            if keyboard.is_pressed("space") or  joystick.get_button(0) == 1:
                              if speed < 0.1 :
                                if walljump == 0:
                                  if speed_y < 0:
                                    impact = 1
                                    impact_last= 5
                                    walljump = 1
                                    speed_y = 4
                                    pygame.mixer.Channel(6).play(b1)
    #WR
    if playerx > -1.5 + colx:
        if playerx < 1.5 + colx:
            if playery > -1.5 - 1.5 + coly:
                if playery < 1.3 - 1.5 + coly:
                    if playerz < -1 + colz:
                        if playerz > -2 + colz:
                            if keyboard.is_pressed("space") or joystick.get_button(0) == 1:
                                if type == 1:
                                    if speed_y < 0:
                                        if speedx > 0.05:
                                            playerz = colz + 1.7
                                            wallrunx = 4
                                            walx = 1
                                        if speedx < -0.05:
                                            playerz = colz + 1.7
                                            wallrunx = 4
                                            walx = 0
    if not speed_y == 0:
        decellx = 0.9
        decellz = 0.9
    if playerx > -1.5 + colx:
        if playerx < 1.5 + colx:
            if playery > -1.5 - 1.5 + coly:
                if playery < 1.3 - 1.5 + coly:
                    if playerz > 1+colz:
                        if playerz < 1.5+colz:
                          if type == 1 or type == 2:
                            playerz = 1.5+colz
                            speedz*=0
                            if keyboard.is_pressed("space") or  joystick.get_button(0) == 1:
                             if speed < 0.1:
                                if walljump == 0:
                                  if speed_y < 0:
                                    impact = 1
                                    impact_last=5
                                    walljump = 1
                                    speed_y = 4
                                    pygame.mixer.Channel(6).play(b1)
    #WR
    if playerx > -1.5 + colx:
        if playerx < 1.5 + colx:
            if playery > -1.5 - 1.5 + coly:
                if playery < 1.3 - 1.5 + coly:
                    if playerz > 1+colz:
                        if playerz < 2+colz:
                            if keyboard.is_pressed("space") or joystick.get_button(0) == 1:
                                if type == 1:
                                    if speed_y < 0:
                                        if speedx > 0.05:
                                            playerz = colz - 1.7
                                            wallrunx = 4
                                            walx = 1
                                        if speedx < -0.05:
                                            playerz = colz - 1.7
                                            wallrunx = 4
                                            walx = 0
    if playerz > -1.4+colz:
        if playerz < 1.4+colz:
            if playery > -1.5 - 1.5 + coly:
                if playery < 1.3 - 1.5 + coly:
                    if playerx > 1+colx:
                        if playerx < 1.5 +colx:
                          if type == 1 or type == 2:
                            playerx = 1.5+colx
                            speedx*=0
                            if keyboard.is_pressed("space") or  joystick.get_button(0) == 1:
                             if speed < 0.1:
                              if speed_y < 0:
                                if walljump == 0:
                                    impact = 1
                                    impact_last=5
                                    walljump = 1
                                    speed_y = 4
                                    pygame.mixer.Channel(6).play(b1)
    if playerz > -1.4+colz:
        if playerz < 1.4+colz:
            if playery > -1.5 - 1.5 + coly:
                if playery < 1.3 - 1.5 + coly:
                    if playerx > 1+colx:
                        if playerx < 2 +colx:
                            if keyboard.is_pressed("space") or joystick.get_button(0) == 1:
                                if type == 1:
                                    if speed_y < 0:
                                        if speedz > 0.05:
                                            playerx = colx + 1.8
                                            wallrunz = 4
                                            walz = 1
                                        if speedz < -0.05:
                                            playerx = colx + 1.8
                                            wallrunz = 4
                                            walz = 0
    if playerz > -1.4+colz:
        if playerz  < 1.4+colz:
            if playery > -1.5 - 1.5+coly:
                if playery < 1.3 - 1.5+coly:
                    if playerx < 1+colx:
                        if playerx > -1.5 +colx:
                          if type == 1 or type == 2:
                            playerx = -1.5+colx
                            speedx*= 0
                            if keyboard.is_pressed("space") or  joystick.get_button(0) == 1:
                             if speed < 0.1:
                              if speed_y < 0:
                                if walljump == 0:
                                    impact = 1
                                    impact_last=5
                                    walljump = 1
                                    speed_y = 4
                                    pygame.mixer.Channel(6).play(b1)
    if playerz > -1.4+colz:
        if playerz  < 1.4+colz:
            if playery > -1.5 - 1.5+coly:
                if playery < 1.3 - 1.5+coly:
                    if playerx < 1+colx:
                        if playerx > -2 +colx:
                            if keyboard.is_pressed("space") or joystick.get_button(0) == 1:
                                if speed_y < 0:
                                    if type == 1:
                                        if speedz > 0.05:
                                            playerx = colx  - 1.8
                                            wallrunz = 4
                                            walz = 1
                                        if speedz < -0.05:
                                            playerx = colx  - 1.8
                                            wallrunz = 4
                                            walz = 0
    gager = 0
    if playery < 1.75 - 1.3+coly:
        if playery > 1.5 - 1.5 +coly:
            if playerx > -1.4+colx:
                if playerx < 1.4+colx:
                    if playerz > -1.4+colz:
                        if playerz < 1.4+colz:
                          if type ==1:
                            gager = 1
                            playery = 1.75 - 1.5+coly
                            speed_y=0
                            walljump = 0
                            decellz = 0.9
                            decellx = 0.9
                            if keyboard.is_pressed('space') or  joystick.get_button(0) == 1:
                                if speed_y == 0:
                                    speed_y = 5 / 1.5 + speed * 3
                          else:
                              if type == 2:
                                  decellz = 0.995
                                  decellx = 0.995
                                  gager = 1
                                  playery = 1.75 - 1.5+coly
                                  speed_y = 0
                                  walljump = 0
                                  if keyboard.is_pressed('space') or joystick.get_button(0) == 1:
                                      if speed_y == 0:
                                          speed_y = 5 / 1.5 + speed * 3
if playery < 2 + coly:
    if playery > -1 + coly:
        if playerx > -1.4 + colx:
            if playerx < 1.4 + colx:
                if playerz > -1.4 + colz:
                    if playerz < 1.4 + colz:
                        if speed_y < 0:
                            if sirol == 0:
                                pygame.mixer.Channel(5).play(r)
                                sirol = 1
                                drol = 1
                                roll = 1
                            isrol = 0
    if playery > -0.7+coly:
        if playery < -2.5 +coly:
            if playerx > -1.4+colx:
                if playerx < 1.4+colx:
                    if playerz > -1.4+colz:
                        if playerz < 1.4+colz:
                            playery = -2.5+coly
                            speed_y=0
if playery <-0 + coly:
    if playery > -1 + coly:
        if playerx > -1.4 + colx:
            if playerx < 1.4 + colx:
                if playerz > -1.4 + colz:
                    if playerz < 1.4 + colz:
                        if speed_y < 0:
                            if sirol == 0:
                                pygame.mixer.Channel(5).play(r)
                                sirol = 1
                                drol = 1
                                roll = 1
                            isrol = 0
    if playery > -0.7+coly:
        if playery < -2 +coly:
            if playerx > -1.4+colx:
                if playerx < 1.4+colx:
                    if playerz > -1.4+colz:
                        if playerz < 1.4+colz:
                            playery = -2.5+coly
                            speed_y=0

def b_coli():
    global bx,bz,by,bsx,bsz,bsy,colx,coly,colz
    if bx > -1.5 + colx:
        if bx < 1.5 + colx:
            if by > -1.4 - 1 +coly:
                if by < 0.25 - 1+coly:
                    if bz < 1 + colz:
                        if bz > -1.5+colz:
                            bz = -1.5+colz
                            bsz *= -0.5
    if bx > -1.5+colx:
        if bx < 1.5+colx:
            if by > -1.4 - 1+coly:
                if by < 0.25 - 1+coly:
                    if bz > 0+colz:
                        if bz <1.5 +colz:
                            bz =1.5
                            bsz*=-0.5
    if bz > -1.5+colz:
        if bz < 1.5+colz:
            if by > -1.4 - 1+coly:
                if by < 0.25 - 1+coly:
                    if bx > 1+colx:
                        if bx < 1.5 +colx:
                            bx = 1.5+colx
                            bsx*=-0.5
    if bz > -1.5+colz:
        if bz  < 1.5+colz:
            if by > -1.4 - 1+coly:
                if by < 0.25 - 1+coly:
                    if bx < 0+colx:
                        if bx > -1.5 +colx:
                            bx = -1.5+colx
                            bsx*= -0.5
    if by < 0+coly:
        if by >-1 +coly:
            if bx > -1.4+colx:
                if bx < 1.4+colx:
                    if bz > -1.4+colz:
                        if bz < 1.4+colz:
                            by = 0+coly
                            if bsy < -0.1:
                              if playerx > bx - 32 * lol:
                                if playerx < bx + 32 * lol:
                                    if playerz > bz - 32 * lol:
                                        if playerz < bz + 32 * lol:
                                            if playery > by - 32 * lol:
                                                if playery < by + 32 * lol:
                                                    pygame.mixer.Channel(0).play(b4)
                                                    if playerx > bx - 25.6 * lol:
                                                        if playerx < bx + 25.6 * lol:
                                                            if playerz > bz - 25.6 * lol:
                                                                if playerz < bz + 25.6 * lol:
                                                                    if playery > by - 25.6 * lol:
                                                                        if playery < by + 25.6 * lol:
                                                                            pygame.mixer.Channel(0).play(b3)
                                                                            if playerx > bx - 19.2 * lol:
                                                                                if playerx < bx + 19.2 * lol:
                                                                                    if playerz > bz - 19.2 * lol:
                                                                                        if playerz < bz + 19.2 * lol:
                                                                                            if playery > by - 19.2 * lol:
                                                                                                if playery < by + 19.2 * lol:
                                                                                                    pygame.mixer.Channel(
                                                                                                        0).play(b2)
                                                                                                    if playerx > bx - 12.8 * lol:
                                                                                                        if playerx < bx + 12.8 * lol:
                                                                                                            if playerz > bz - 12.8 * lol:
                                                                                                                if playerz < bz + 12.8 * lol:
                                                                                                                    if playery > by - 12.8 * lol:
                                                                                                                        if playery < by + 12.8 * lol:
                                                                                                                            pygame.mixer.Channel(
                                                                                                                                0).play(
                                                                                                                                b1)
                            bsy *= -0.9

def e_coli():
    global esy, esx, esz, ex, ey, ez, colx, coly, colz
    if sy < 0 + coly:
        if sy > -1 + coly:
            if playerx > -1.4 + colx:
                if playerx < 1.4 + colx:
                    if playerz > -1.4 + colz:
                        if playerz < 1.4 + colz:
                            ey = 0 + coly


def e_coli():
    global ex, ez, ey, esx, esz, esy, colx, coly, colz
    if ex > -1.5 + colx:
        if ex < 1.5 + colx:
            if ey > -1.4 - 1 + coly:
                if ey < 0.25 - 1 + coly:
                    if ez < 1 + colz:
                        if ez > -1.5 + colz:
                            ez = -1.5 + colz
                            esz = 0
    if ex > -1.5 + colx:
        if ex < 1.5 + colx:
            if ey > -1.4 - 1 + coly:
                if ey < 0.25 - 1 + coly:
                    if ez > 0 + colz:
                        if ez < 1.5 + colz:
                            ez = 1.5
                            esz = 0
    if ez > -1.5 + colz:
        if ez < 1.5 + colz:
            if ey > -1.4 - 1 + coly:
                if ey < 0.25 - 1 + coly:
                    if ex > 1 + colx:
                        if ex < 1.5 + colx:
                            ex = 1.5 + colx
                            esx = 0
    if ez > -1.5 + colz:
        if ez < 1.5 + colz:
            if ey > -1.4 - 1 + coly:
                if ey < 0.25 - 1 + coly:
                    if ex < 0 + colx:
                        if ex > -1.5 + colx:
                            ex = -1.5 + colx
                            esx= 0
    if ey < 0 + coly:
        if ey > -1 + coly:
            if ex > -1.4 + colx:
                if ex < 1.4 + colx:
                    if ez > -1.4 + colz:
                        if ez < 1.4 + colz:
                            ey = 0 + coly
                            if esy < -0.1:
                                ey = 0 + coly
                                esy = 0




#lists
i = 0
block_info = [0, 0, 0, 1, 1.5, 0.0, 0.0, 1, 3.0, 0.0, 0.0, 1, 3.0, 0.0, -1.5, 1, 1.5, 0.0, -1.5, 1, 0.0, 0.0, -1.5, 1, -1.5, 0.0, -1.5, 1, -1.5, 0.0, 0.0, 1, -1.5, 0.0, -3.0, 1, 0.0, 0.0, -3.0, 1, 1.5, 0.0, -3.0, 1, 3.0, 0.0, -3.0, 1, 3.0, 0.0, -3.0, 1, 3.0, 0.0, -4.5, 1, 1.5, 0.0, -4.5, 1, 0.0, 0.0, -4.5, 1, -1.5, 0.0, -4.5, 1, 3.0, 0.0, 1.5, 1, 1.5, 0.0, 1.5, 1, 0.0, 0.0, 1.5, 1, -1.5, 0.0, 1.5, 1, 3.0, 0.0, 3.0, 1, 1.5, 0.0, 3.0, 1, 0.0, 0.0, 3.0, 1, -1.5, 0.0, 3.0, 1, -1.5, 1.5, 4.5, 1, 0.0, 1.5, 4.5, 1, 1.5, 1.5, 4.5, 1, 3.0, 1.5, 4.5, 1, 3.0, 3.0, 4.5, 1, 1.5, 3.0, 4.5, 1, 0.0, 3.0, 4.5, 1, -1.5, 3.0, 4.5, 1, -1.5, 3.0, 6.0, 1, 0.0, 3.0, 6.0, 1, 1.5, 3.0, 6.0, 1, 3.0, 3.0, 6.0, 1, 4.5, 1.5, 4.5, 1, 6.0, 1.5, 4.5, 1, 7.5, 1.5, 4.5, 1, 9.0, 1.5, 4.5, 1, 9.0, 3.0, 4.5, 1, 7.5, 3.0, 4.5, 1, 6.0, 3.0, 4.5, 1, 4.5, 3.0, 4.5, 1, 4.5, 3.0, 6.0, 1, 6.0, 3.0, 6.0, 1, 7.5, 3.0, 6.0, 1, 9.0, 3.0, 6.0, 1, 9.0, 3.0, 7.5, 1, 7.5, 3.0, 7.5, 1, 6.0, 3.0, 7.5, 1, 4.5, 3.0, 7.5, 1, 3.0, 3.0, 7.5, 1, 1.5, 3.0, 7.5, 1, 0.0, 3.0, 7.5, 1, -1.5, 3.0, 7.5, 1, -1.5, 3.0, 9.0, 1, 0.0, 3.0, 9.0, 1, 1.5, 3.0, 9.0, 1, 3.0, 3.0, 9.0, 1, 4.5, 3.0, 9.0, 1, 6.0, 3.0, 9.0, 1, 7.5, 3.0, 9.0, 1, 9.0, 3.0, 9.0, 1, 9.0, 3.0, 10.5, 1, 9.0, 3.0, 10.5, 1, 7.5, 3.0, 10.5, 1, 6.0, 3.0, 10.5, 1, 4.5, 3.0, 10.5, 1, 3.0, 3.0, 10.5, 1, 1.5, 3.0, 10.5, 1, 0.0, 3.0, 10.5, 1, -1.5, 3.0, 10.5, 1, -1.5, 3.0, 12.0, 1, 0.0, 3.0, 12.0, 1, 1.5, 3.0, 12.0, 1, 3.0, 3.0, 12.0, 1, 4.5, 3.0, 12.0, 1, 6.0, 3.0, 12.0, 1, 7.5, 3.0, 12.0, 1, 9.0, 3.0, 12.0, 1, 9.0, 3.0, 13.5, 1, 7.5, 3.0, 13.5, 1, 6.0, 3.0, 13.5, 1, 4.5, 3.0, 13.5, 1, 3.0, 3.0, 13.5, 1, 1.5, 3.0, 13.5, 1, 1.5, 3.0, 13.5, 1, 0.0, 3.0, 13.5, 1, -1.5, 3.0, 13.5, 1, 9.0, 3.0, 15.0, 1, 9.0, 3.0, 16.5, 1, 9.0, 3.0, 18.0, 1, 9.0, 3.0, 19.5, 1, 9.0, 3.0, 21.0, 1, 9.0, 3.0, 22.5, 1, 9.0, 3.0, 24.0, 1, 9.0, 3.0, 25.5, 1, 9.0, 4.5, 25.5, 1, 9.0, 4.5, 24.0, 1, 9.0, 4.5, 22.5, 1, 9.0, 4.5, 21.0, 1, 9.0, 4.5, 19.5, 1, 9.0, 4.5, 18.0, 1, 9.0, 4.5, 16.5, 1, 9.0, 4.5, 15.0, 1, 9.0, 4.5, 13.5, 1, 9.0, 6.0, 25.5, 1, 9.0, 6.0, 24.0, 1, 9.0, 6.0, 22.5, 1, 9.0, 6.0, 21.0, 1, 9.0, 6.0, 19.5, 1, 9.0, 6.0, 18.0, 1, 9.0, 6.0, 16.5, 1, 9.0, 6.0, 15.0, 1, 9.0, 6.0, 13.5, 1, 9.0, 7.5, 25.5, 1, 9.0, 7.5, 25.5, 1, 9.0, 7.5, 24.0, 1, 9.0, 7.5, 22.5, 1, 9.0, 7.5, 21.0, 1, 9.0, 7.5, 19.5, 1, 9.0, 7.5, 18.0, 1, 9.0, 7.5, 16.5, 1, 9.0, 7.5, 15.0, 1, 9.0, 7.5, 13.5, 1, 6.0, 1.5, 37.5, 1, 6.0, 1.5, 37.5, 1, 4.5, 1.5, 37.5, 1, 3.0, 1.5, 37.5, 1, 1.5, 1.5, 37.5, 1, 7.5, 1.5, 37.5, 1, 7.5, 1.5, 39.0, 1, 6.0, 1.5, 39.0, 1, 4.5, 1.5, 39.0, 1, 3.0, 1.5, 39.0, 1, 1.5, 1.5, 39.0, 1, 1.5, 1.5, 40.5, 1, 3.0, 1.5, 40.5, 1, 4.5, 1.5, 40.5, 1, 6.0, 1.5, 40.5, 1, 7.5, 1.5, 40.5, 1, 7.5, 1.5, 42.0, 1, 6.0, 0.0, 42.0, 1, 6.0, 1.5, 42.0, 1, 4.5, 1.5, 42.0, 1, 3.0, 1.5, 42.0, 1, 1.5, 1.5, 42.0, 1, 7.5, 1.5, 43.5, 1, 6.0, 1.5, 43.5, 1, 4.5, 1.5, 43.5, 1, 3.0, 1.5, 43.5, 1, 1.5, 1.5, 43.5, 1, 1.5, 1.5, 45.0, 1, 3.0, 1.5, 45.0, 1, 4.5, 1.5, 45.0, 1, 6.0, 1.5, 45.0, 1, 7.5, 1.5, 45.0, 1, 9.0, 1.5, 45.0, 1, 9.0, 1.5, 43.5, 1, 9.0, 1.5, 40.5, 1, 9.0, 1.5, 39.0, 1, 9.0, 1.5, 42.0, 1, 9.0, 1.5, 37.5, 1, 10.5, 1.5, 37.5, 1, 10.5, 1.5, 39.0, 1, 10.5, 1.5, 40.5, 1, 10.5, 1.5, 42.0, 1, 10.5, 1.5, 43.5, 1, 10.5, 1.5, 45.0, 1, 12.0, 1.5, 45.0, 1, 12.0, 1.5, 43.5, 1, 12.0, 1.5, 42.0, 1, 12.0, 1.5, 40.5, 1, 13.5, 1.5, 40.5, 1, 13.5, 1.5, 42.0, 1, 13.5, 1.5, 43.5, 1, 13.5, 1.5, 45.0, 1, 13.5, 1.5, 46.5, 1, 12.0, 1.5, 46.5, 1, 10.5, 1.5, 46.5, 1, 9.0, 1.5, 46.5, 1, 7.5, 1.5, 46.5, 1, 7.5, 1.5, 46.5, 1, 6.0, 1.5, 46.5, 1, 4.5, 1.5, 46.5, 1, 4.5, 1.5, 48.0, 1, 6.0, 1.5, 48.0, 1, 7.5, 1.5, 48.0, 1, 9.0, 1.5, 48.0, 1, 10.5, 1.5, 48.0, 1, 12.0, 1.5, 48.0, 1, 13.5, 1.5, 48.0, 1, 13.5, 1.5, 49.5, 1, 12.0, 1.5, 49.5, 1, 10.5, 1.5, 49.5, 1, 7.5, 1.5, 49.5, 1, 6.0, 1.5, 49.5, 1, 4.5, 1.5, 49.5, 1, 9.0, 1.5, 49.5, 1, 13.5, 1.5, 51.0, 1, 12.0, 1.5, 51.0, 1, 10.5, 1.5, 51.0, 1, 9.0, 1.5, 51.0, 1, 7.5, 1.5, 51.0, 1, 6.0, 1.5, 51.0, 1, 4.5, 1.5, 51.0, 1, 13.5, 1.5, 52.5, 1, 10.5, 1.5, 52.5, 1, 12.0, 1.5, 52.5, 1, 9.0, 1.5, 52.5, 1, 7.5, 1.5, 52.5, 1, 6.0, 1.5, 52.5, 1, 4.5, 1.5, 52.5, 1, 4.5, 3.0, 52.5, 1, 6.0, 3.0, 52.5, 1, 7.5, 3.0, 52.5, 1, 9.0, 3.0, 52.5, 1, 10.5, 3.0, 52.5, 1, 12.0, 3.0, 52.5, 1, 13.5, 3.0, 52.5, 1, 4.5, 4.5, 52.5, 1, 6.0, 4.5, 52.5, 1, 7.5, 4.5, 52.5, 1, 9.0, 4.5, 52.5, 1, 10.5, 4.5, 52.5, 1, 12.0, 4.5, 52.5, 1, 13.5, 4.5, 52.5, 1, 13.5, 6.0, 52.5, 1, 12.0, 6.0, 52.5, 1, 10.5, 6.0, 52.5, 1, 9.0, 6.0, 52.5, 1, 7.5, 6.0, 52.5, 1, 6.0, 6.0, 52.5, 1, 4.5, 6.0, 52.5, 1, 4.5, 6.0, 54.0, 1, 6.0, 6.0, 54.0, 1, 7.5, 6.0, 54.0, 1, 9.0, 6.0, 54.0, 1, 10.5, 6.0, 54.0, 1, 12.0, 6.0, 54.0, 1, 13.5, 6.0, 54.0, 1, 12.0, 6.0, 55.5, 1, 13.5, 6.0, 55.5, 1, 10.5, 6.0, 55.5, 1, 9.0, 6.0, 55.5, 1, 7.5, 6.0, 55.5, 1, 6.0, 6.0, 55.5, 1, 4.5, 6.0, 55.5, 1, 6.0, 6.0, 57.0, 1, 4.5, 6.0, 57.0, 1, 7.5, 6.0, 57.0, 1, 9.0, 6.0, 57.0, 1, 10.5, 6.0, 57.0, 1, 12.0, 6.0, 57.0, 1, 13.5, 6.0, 57.0, 1, 13.5, 6.0, 58.5, 1, 12.0, 6.0, 58.5, 1, 10.5, 6.0, 58.5, 1, 9.0, 6.0, 58.5, 1, 7.5, 6.0, 58.5, 1, 6.0, 6.0, 58.5, 1, 4.5, 6.0, 58.5, 1, 4.5, 6.0, 60.0, 1, 6.0, 6.0, 60.0, 1, 7.5, 6.0, 60.0, 1, 9.0, 6.0, 60.0, 1, 10.5, 6.0, 60.0, 1, 12.0, 6.0, 60.0, 1, 13.5, 6.0, 60.0, 1, 13.5, 6.0, 61.5, 1, 12.0, 6.0, 61.5, 1, 10.5, 6.0, 61.5, 1, 9.0, 6.0, 61.5, 1, 7.5, 6.0, 61.5, 1, 6.0, 6.0, 61.5, 1, 4.5, 6.0, 61.5, 1]

i = 0
cubes = {}
for i in range(0, len(block_info) - 2, 4):
    name = f"cube{i//4}"
    cubes[name] = Entity(
        model='cube',
        position=(block_info[i], block_info[i+1], block_info[i+2]),
        scale=(1.5, 1.5, 1.5),
        rotation=(0, 0, 0),
        texture='tex.png',
        color=color.rgb(50, 50, 70),
    )
i = 0
cs = {}
for i in range(0, len(block_info) - 2, 4):
    name = f"cube{i//4}"
    cs[name] = Entity(
        model='cube',
        position=(block_info[i], block_info[i+1], block_info[i+2]),
        scale=(1.5, 1.5, 1.5),
        rotation=(0, 0, 0),
        texture='costume1 (2).png',
        color=color.rgb(50, 50, 70),
    )

#wait for absolutely no fucking reason
wait1 = 0
while wait1 < 160:
    wait1 = wait1 + 1
pi = 0
pause = 1
stop = 1
dob_tim = 0
ap = 0
slow = 1
slowp = 0
light1 = 0
lp = 0
intro = 1
y_text_intro = 0
gags = 0
anim_text = 0
edir = 0
def update():
 global intro
 if intro == 1:
    global block_info
    global y_text_intro
    global ini
    global gags
    global speed_y
    global playery
    global speedx
    global speedz
    global playerx
    global playerz
    global decellx
    global decellz
    global camx
    global camy
    global camz
    global dx
    global dy
    global dz
    global bx
    global by
    global bz
    global bsx
    global bsy
    global bsz
    global frame
    global dir
    global speed
    global gb
    global gbt
    global bdx
    global bdy
    global bsz
    global frame
    global dir
    global speed
    global press
    global cox
    global coz
    global utg
    global xx
    global zz
    global debug
    global whaid
    global camyy
    global spex
    global speedxxxx
    global result
    global framelast
    global sframe
    global s
    global e
    global roll
    global isrol
    global drol
    global slide
    global tree_frame
    global tree_sprite
    global TICK
    global editor
    global xxx
    global zzz
    global yyy
    global sirol
    global landed
    global pressed
    global spin
    global sf
    global lpress
    global llpress
    global yy
    global dyy
    global anim
    global colx
    global coly
    global colz
    global walljump
    global sy
    global s45
    global impact
    global impact_last
    global block_info
    global wallrunz
    global wallrunx
    global walz
    global walx
    global yyyy
    global bcaw
    global w
    global wap
    global bcas
    global sap
    global ss
    global gager
    global yaye
    global gagle
    global dir_y
    global rots
    global zoom
    global aii
    global re
    global re2
    global type
    global pause
    global pi
    global dob_tim
    global stop
    global ap
    global slow
    global slowp
    global light1
    global anim_text
    global ex
    global ey
    global ez
    global esx
    global esy
    global esz

    if ini > 0:
        gags += 0.05
    if gags > 2:
        ini = 0
    y_text_intro += 0.0025 / 0.25
    message1.y = y_text_intro / 20 + 0.35 - 0.4
    m1.y = y_text_intro / 20 + 0.3 - 0.4
    message2.y = y_text_intro / 20 + 0.35 - 0.4 - 0.05 - 0.05
    m2.y = y_text_intro / 20 + 0.3 - 0.4 - 0.05 - 0.05
    message3.y = y_text_intro / 20 + 0.25 - 0.4 - 0.05 - 0.05
    message4.y = y_text_intro / 20 + 0.2 - 0.4 - 0.05 - 0.05
    m4.y = y_text_intro / 20 + 0.2 - 0.45 - 0.05 - 0.05
    message5.y = y_text_intro / 20 + 0.15 - 0.4 - 0.05 - 0.05 - 0.05
    m6.y = y_text_intro / 20 + 0.1 - 0.4 - 0.05 - 0.05 - 0.05
    m66.y = y_text_intro / 20 + 0.1 - 0.4 - 0.05 - 0.05 - 0.05 - 0.05
    clock.tick(30)

    if message1.y > -0.1 * gags and message1.y < 0.1 * gags :
        message1.color = color.rgb(0, 0, 0)
        if message1.y > -0.08 * gags and message1.y < 0.08 * gags:
            message1.color = color.rgb(0.2, 0.2, 0.3)
            if message1.y > -0.06 * gags and message1.y < 0.06 * gags:
                message1.color = color.rgb(0.4, 0.4, 0.5)
                if message1.y > -0.04 * gags and message1.y < 0.04 * gags:
                    message1.color = color.rgb(0.6, 0.6, 0.7)
                    if message1.y > -0.02 * gags and message1.y < 0.02 * gags:
                        message1.color = color.rgb(0.8, 0.8, 1)
    else:
        message1.color = color.rgb(0, 0, 0)
    if m1.y > -0.1 * gags and m1.y < 0.1  * gags:
        m1.color = color.rgb(0, 0, 0)
        if m1.y > -0.08  * gags and m1.y < 0.08 * gags:
            m1.color = color.rgb(0.2, 0.2, 0.3)
            if m1.y > -0.06  * gags and m1.y < 0.06 * gags :
                m1.color = color.rgb(0.4, 0.4, 0.5)
                if m1.y > -0.04  * gags and m1.y < 0.04 * gags :
                    m1.color = color.rgb(0.6, 0.6, 0.7)
                    if m1.y > -0.02  * gags and m1.y < 0.02 * gags :
                        m1.color = color.rgb(0.8, 0.8, 1)
    else:
        m1.color = color.rgb(0, 0, 0)
    if message2.y > -0.1  * gags and message2.y < 0.1 * gags  :
        message2.color = color.rgb(0, 0, 0)
        if message2.y > -0.08  * gags and message2.y < 0.08 * gags :
            message2.color = color.rgb(0.2, 0.2, 0.3)
            if message2.y > -0.06 * gags  and message2.y < 0.06 * gags :
                message2.color = color.rgb(0.4, 0.4, 0.5)
                if message2.y > -0.04  * gags and message2.y < 0.04 * gags :
                    message2.color = color.rgb(0.6, 0.6, 0.7)
                    if message2.y > -0.02  * gags and message2.y < 0.02 * gags :
                        message2.color = color.rgb(0.8, 0.8, 1)
    else:
        message2.color = color.rgb(0, 0, 0)
    if message3.y > -0.1 * gags  and message3.y < 0.1 * gags :
        message3.color = color.rgb(0, 0, 0)
        if message3.y > -0.08  * gags and message3.y < 0.08 * gags :
            message3.color = color.rgb(0.2, 0.2, 0.3)
            if message3.y > -0.06  * gags and message3.y < 0.06 * gags :
                message3.color = color.rgb(0.4, 0.4, 0.5)
                if message3.y > -0.04  * gags and message3.y < 0.04 * gags :
                    message3.color = color.rgb(0.6, 0.6, 0.7)
                    if message3.y > -0.02 * gags  and message3.y < 0.02 * gags :
                        message3.color = color.rgb(0.8, 0.8, 1)
    else:
        message3.color = color.rgb(0, 0, 0)
    if m2.y > -0.1  * gags and m2.y < 0.1 * gags  :
        m2.color = color.rgb(0, 0, 0)
        if m2.y > -0.08 * gags  and m2.y < 0.08 * gags :
            m2.color = color.rgb(0.2, 0.2, 0.3)
            if m2.y > -0.06  * gags and m2.y < 0.06 * gags :
                m2.color = color.rgb(0.4, 0.4, 0.5)
                if m2.y > -0.04  * gags and m2.y < 0.04 * gags :
                    m2.color = color.rgb(0.6, 0.6, 0.7)
                    if m2.y > -0.02  * gags and m2.y < 0.02 * gags :
                        m2.color = color.rgb(0.8, 0.8, 1)
    else:
        m2.color = color.rgb(0, 0, 0)
    if message4.y > -0.1  * gags and message4.y < 0.1  * gags :
        message4.color = color.rgb(0, 0, 0)
        if message4.y > -0.08  * gags and message4.y < 0.08 * gags :
            message4.color = color.rgb(0.2, 0.2, 0.3)
            if message4.y > -0.06 * gags  and message4.y < 0.06 * gags :
                message4.color = color.rgb(0.4, 0.4, 0.5)
                if message4.y > -0.04 * gags  and message4.y < 0.04 * gags :
                    message4.color = color.rgb(0.6, 0.6, 0.7)
                    if message4.y > -0.02  * gags and message4.y < 0.02 * gags :
                        message4.color = color.rgb(0.9, 0.8, 1)
    else:
        message4.color = color.rgb(0, 0, 0)
    if m4.y > -0.1  * gags and m4.y < 0.1 * gags  :
        m4.color = color.rgb(0, 0, 0)
        if m4.y > -0.08 * gags  and m4.y < 0.08 * gags :
            m4.color = color.rgb(0.2, 0.2, 0.3)
            if m4.y > -0.06  * gags and m4.y < 0.06 * gags :
                m4.color = color.rgb(0.4, 0.4, 0.5)
                if m4.y > -0.04  * gags and m4.y < 0.04 * gags :
                    m4.color = color.rgb(0.6, 0.6, 0.7)
                    if m4.y > -0.02  * gags and m4.y < 0.02 * gags :
                        m4.color = color.rgb(0.9, 0.8, 1)
    else:
        m4.color = color.rgb(0, 0, 0)
    if message5.y > -0.1  * gags and message5.y < 0.1  * gags :
        message5.color = color.rgb(0, 0, 0)
        if message5.y > -0.08  * gags and message5.y < 0.08 * gags :
            message5.color = color.rgb(0.2, 0.2, 0.3)
            if message5.y > -0.06 * gags  and message5.y < 0.06 * gags :
                message5.color = color.rgb(0.4, 0.4, 0.5)
                if message5.y > -0.04 * gags  and message5.y < 0.04 * gags :
                    message5.color = color.rgb(0.6, 0.6, 0.7)
                    if message5.y > -0.02  * gags and message5.y < 0.02 * gags :
                        message5.color = color.rgb(0.9, 0.8, 1)
    else:
        message5.color = color.rgb(0, 0, 0)

    if m66.y > -0.1  * gags and m66.y < 0.1  * gags :
        m6.color = color.rgb(0, 0, 0)
        m66.color = color.rgb(0, 0, 0)
        if m66.y > -0.08  * gags and m66.y < 0.08 * gags :
            m6.color = color.rgb(0.3, 0.2, 0.2)
            m66.color = color.rgb(0.3, 0.2, 0.2)
            if m66.y > -0.06 * gags  and m66.y < 0.06 * gags :
                m6.color = color.rgb(0.5, 0.4, 0.4)
                m66.color = color.rgb(0.5, 0.4, 0.4)
                if m6.y > -0.04 * gags  and m66.y < 0.04 * gags :
                    m6.color = color.rgb(0.7, 0.6, 0.6)
                    m66.color = color.rgb(0.7, 0.6, 0.6)
                    if m66.y > -0.02  * gags and m66.y < 0.02 * gags :
                        m6.color = color.rgb(1, 0.8, 0.8)
                        m66.color = color.rgb(1, 0.8, 0.8)
    else:
        m6.color = color.rgb(0, 0, 0)
        m66.color = color.rgb(0, 0, 0)
    if y_text_intro > 11.3 :
        anim_text -= 0.5
        ini -= 1
        y_text_intro = 11.3
        m6.color = color.rgb(0.8, 0.8, 1)
        m66.color = color.rgb(0.8, 0.8, 1)
        if anim_text == -1:
            m6.color = color.rgb(0, 0,0)
            m66.color = color.rgb(0, 0, 0)
        if anim_text == -2:
            m6.color = color.rgb(1, 1,1)
            m66.color = color.rgb(0, 0, 0)
        if anim_text == -3:
            m66.color = color.rgb(1, 1,1)
            m6.color = color.rgb(0, 0, 0)
        if anim_text == -4:
                m6.color = color.rgb(1, 1, 1)
                m66.color = color.rgb(1, 1, 1)
        if anim_text == -5:
                m6.color = color.rgb(1, 0, 0)
                m66.color = color.rgb(1, 0, 0)
        if anim_text < -6:
                m6.color = color.rgb(1, 0.9, 0.9)
                m66.color = color.rgb(1, 0.9, 0.9)

    i = 0
    while i < len(block_info) / 4:
        index = int(i * 4)
        cubes['cube' + str(i)].x = 1000
        cubes['cube' + str(i)].x = 1000
        cubes['cube' + str(i)].x = 1000
        i += 1

    i = 0
    while i < len(block_info) / 4:
        index = int(i * 4)

        cs['cube' + str(i)].x = 1000
        cs['cube' + str(i)].x = 1000
        cs['cube' + str(i)].x = 1000
        i += 1
    if keyboard.is_pressed('space') or joystick.get_button(1) == 1:
        intro = 0
        #pygame.mixer.Channel(17).play(bgm1, loops=-1)
    if keyboard.is_pressed('enter') or joystick.get_button(2) == 1:
        intro = 0
        #pygame.mixer.Channel(17).play(bgm1, loops=-1)
    obj.y = 1000000
    obj.scale = (1.5 - yyyy / 10, yyyy / 5 + 1.5, 1.5 - yyyy / 10)
    obj.shad.y = 1000000
    obj.shad.scale = (1.5 - yyyy / 10, yyyy / 5 + 1.5, 1.5 - yyyy / 10)
    obj.z = 1000000
    obj.shad.z = 1000000
    obj.x = 1000000
    obj.shad.x = 1000000
    obj.reflect.y = 1000000
    obj.reflect.scale = (1.5 - yyyy / 10, yyyy / 5 + 1.5, 1.5 - yyyy / 10)
    obj.shad.ref.y = 1000000
    obj.shad.ref.scale = (1.5 - yyyy / 10, yyyy / 5 + 1.5, 1.5 - yyyy / 10)
    obj.reflect.z = 1000000
    obj.shad.ref.z = 1000000
    obj.reflect.x = 1000000
    obj.shad.ref.x = 1000000
    block.y = 1000000
    block.z = 1000000
    block.x = 1000000
    ball.y = 1000000
    ball.shad.y = 1000000
    ball.z = 1000000
    ball.shad.z = 1000000
    ball.x = 1000000
    ball.shad.x = 1000000
    ball.ref.y = 1000000
    ball.ref.shad.y = 1000000
    ball.ref.z = 1000000
    ball.ref.shad.z = 1000000
    ball.ref.shad.x = 1000000
    ball.ref.x = 1000000
    light_1.y = 1000000

 else:
  global edir
  global speed_y
  global playery
  global speedx
  global speedz
  global playerx
  global playerz
  global decellx
  global decellz
  global camx
  global camy
  global camz
  global dx
  global dy
  global dz
  global bx
  global by
  global bz
  global bsx
  global bsy
  global bsz
  global frame
  global dir
  global speed
  global gb
  global gbt
  global bdx
  global bdy
  global bsz
  global frame
  global dir
  global speed
  global press
  global cox
  global coz
  global utg
  global xx
  global zz
  global debug
  global whaid
  global camyy
  global spex
  global speedxxxx
  global result
  global framelast
  global sframe
  global s
  global e
  global roll
  global isrol
  global drol
  global slide
  global tree_frame
  global tree_sprite
  global TICK
  global editor
  global xxx
  global zzz
  global yyy
  global sirol
  global landed
  global pressed
  global spin
  global sf
  global lpress
  global llpress
  global yy
  global dyy
  global anim
  global colx
  global coly
  global colz
  global walljump
  global sy
  global s45
  global impact
  global impact_last
  global wallrunz
  global wallrunx
  global walz
  global walx
  global bcaw
  global w
  global wap
  global bcas
  global sap
  global ss
  global gager
  global yaye
  global gagle
  global dir_y
  global rots
  global zoom
  global aii
  global re
  global re2
  global type
  global pause
  global pi
  global dob_tim
  global stop
  global ap
  global slow
  global slowp
  global light1
  global lp
  global eh
  if playerx > ex:
      if slow == 1 :
            esx += 0.02
      else:
          esx += 0.01
  if playerx < ex:
      if slow == 1:
            esx += -0.02
      else:
          esx += -0.01
  if playerz > ez:
      if slow == 1:
            esz += 0.02
      else:
          esz += 0.01
  if playerz < ez:
      if slow == 1:
            esz += -0.02
      else:
          esz += -0.01
  angle = math.atan2(esz, esx)
  edir = math.degrees(angle)
  enemy.rotation_y = round ( edir * -1  / 16) * 16
  esx *= 0.98
  esz *= 0.98
  if slow == 1 :
      esy -= 0.03
  else:
      esy -= 0.015
  ey += esy
  if ey < -1.5:
      ey = -1.5
      esy = 0
  i = 0
  for i in range(0, len(block_info) - 2, 4):
      colx = block_info[i]
      coly = block_info[i + 1]
      colz = block_info[i + 2]
      type = block_info[i + 3]
      if colx + 3 > ex:
          if colx - 3 < ex:
              if colz + 3 > ez:
                  if colz - 3 < ez:
                      if coly - 3 < ey:
                          if coly + 3 > ey:
                              e_coli()

  if playery - 2 > ey :
      if esy == 0 :
          if slow == 1:
              esy = 0.5
          else:
              esy = 0.5 / 2
  ex += esx
  ez += esz

  if wallrunx == 0 or wallrunz == 0:
      speed_y = 3
  if ex + 8 + esx + esx + esx + esx > playerx and ex - 8 + esx + esx + esx + esx < playerx and ez + 8 + esz + esz > playerz and ez - 8  + esz + esz + esz + esz< playerz and ey + 3 > playery and ey - 3 < playery:
        slow = -1
        if slowp == 0:
                        slowp = 1
                        if slow == 1 :
                            speedx *= 2
                            speedz *= 2
                            speed_y *= 2
                        if slow == -1 :
                            speedx /= 2
                            speedz /= 2
                            speed_y/=2
  else:
      slow = 1
      slowp = 0

  if ex + 1 > playerx and ex - 1 < playerx and ez + 1 > playerz and ez - 1< playerz and ey + 1.5 > playery and ey - 1.5 < playery:
                if eh == 0:
                    cox = math.cos(math.radians(dir)) * -0.2
                    coz = math.sin(math.radians(dir)) * -0.2
                    speedx = cox
                    speedz = coz
                    eh = 1
                    impact_last = 5
                    playery += 0.1
                    speed_y = 4
  else:
          eh = 0
  if ex + 5 > playerx and ex - 5 < playerx and ez + 5 > playerz and ez - 5 < playerz and ey + 6 > playery and ey - 6 < playery:
      if mouse.left == 1 or joystick.get_button(1) == 1:
          cox = math.cos(math.radians(dir)) * 1
          coz = math.sin(math.radians(dir)) * 1
          esx = cox
          esz = coz
          esy = 0.3





  pi -= 1
  dob_tim -= 1
  ap -= 1
  if slow == -1 :
      playerx += speedx * time.dt * -50 / 2
      playerz += speedz * time.dt * -50 / 2
      ex += esx * -0.5
      ez += esz * -0.5
      ey -= esy / 2

  if keyboard.is_pressed("enter"):
      if pi < 0 :
          pause *= -1
          if pause == 1:
              pygame.mixer.Channel(14).play(up)
              pygame.mixer.unpause()
          if pause == -1:
              pygame.mixer.Channel(14).play(p)
              time.sleep(0.3)
              pygame.mixer.pause()
          pi = 10


  if pause == 1:
    i = 0
    for i in range(0, len(block_info) - 2, 4):
          colx = block_info[i]
          coly = block_info[i + 1]
          colz = block_info[i + 2]
          type = block_info[i + 3]
          if colx + 3 > playerx:
              if colx - 3 < playerx:
                  if colz + 3 > playerz:
                      if colz - 3 < playerz:
                          if coly - 3 < playery:
                              if coly + 3 > playery:
                                  coli()
    controls()
    playerx -= speedx
    playerz -= speedz
    playery -= speed_y
    playerx += speedx /3
    playerz += speedz /3
    playery += speed_y /3
    if impact_last > 0 :
        ex -= esx / 2
        ez -= esz / 2
        ey -= esy / 2

    i = 0
    colx = block_info[i]
    coly = block_info[i + 1]
    colz = block_info[i + 2]
    type = block_info[i + 3]
    if colx + 3 > playerx:
        if colx - 3 < playerx:
            if colz + 3 > playerz:
                if colz - 3 < playerz:
                    if coly - 3 < playery:
                        if coly + 3 > playery:
                            coli()

    playerx += speedx / 3
    playerz += speedz / 3
    playery += speed_y / 3

    i = 0
    colx = block_info[i]
    coly = block_info[i + 1]
    colz = block_info[i + 2]
    type = block_info[i + 3]
    if colx + 3 > playerx:
        if colx - 3 < playerx:
            if colz + 3 > playerz:
                if colz - 3 < playerz:
                    if coly - 3 < playery:
                        if coly + 3 > playery:
                            coli()

    playerx += speedx / 3
    playerz += speedz / 3
    playery += speed_y / 3

    i = 0
    colx = block_info[i]
    coly = block_info[i + 1]
    colz = block_info[i + 2]
    type = block_info[i + 3]
    if colx + 3 > playerx:
        if colx - 3 < playerx:
            if colz + 3 > playerz:
                if colz - 3 < playerz:
                    if coly - 3 < playery:
                        if coly + 3 > playery:
                            coli()


    re2 -= 0.5
    aii +=1
    if aii < 60 :
        rots += 1
        dir_y = re
        zoom += 0.5

    TICK += 1
    impact -= 0.5




    impact_last-=0.5
    if round(speed_y) == 0 :
        anim += speed * 40

    if keyboard.is_pressed('shift'):
        dyy = -5 - yy
        yy += dyy *0.05
    else:
        dyy = 0 - yy
        yy += dyy * 0.05

    if not round(speed_y) ==0:
        frame = 11



    tree_frame += 0.1

    if mouse.left or joystick.get_button(2) == 1:
      if llpress == 0:
       if lpress == 0:
        lpress = 1
        llpress = 1
        cox = math.cos(math.radians(dir)) * 0.6
        coz = math.sin(math.radians(dir)) * 0.6
        speedx = cox
        speedz = coz
        if round(speed_y) == 0:
                speed_y = 2
        else:
            speed_y = 1
    else:
        llpress = 0



    slide = 0
    if keyboard.is_pressed('shift') or joystick.get_button(5) == 1:
        slide = 1
        if not keyboard.is_pressed('q'):
            if speed_y == 0 and drol == 0:
                slide = 1
                decellx = 0.99
                decellz = 0.99
                # Stop movement input
                speedx *= decellx
                speedz *= decellz

                # Flatten scale for sliding visuals
                obj.scale = (3, 0.5, 3)
                obj.shad.scale = (3, 0.5, 3)
                obj.reflect.scale = (3, 0.5, 3)
                obj.shad.ref.scale = (3, 0.5, 3)
                obj.y = playery - camy - 1
                obj.shad.y = playery - camy - 1
                obj.reflect.y = 0 - playery - camy - 5 + 0.5
                obj.shad.ref.y = 0 - playery - camy - 5 + 0.5
    else:
      obj.scale = (1.5, 1.5, 1.5)
      obj.shad.scale = (1.5, 1.5, 1.5)
      obj.reflect.scale = (1.5, 1.5, 1.5)
      obj.shad.ref.scale = (1.5, 1.5, 1.5)

    if drol == 1:
        roll += speed * 7.5 + 7.5
    if roll > 360:
        drol = 0
        roll = 0
        sirol=0
    if mouse.right or joystick.get_button(1) == 1:
      if e == 0:
       if ex + 1.5 > playerx and ex - 1.5 < playerx and ez + 1.5 > playerz and ez - 1.5 < playerz and ey + 2 > playery and ey - 2 < playery:
        pass
       else:
        e = 1
        cox = math.cos(math.radians(dir)) * 0.5
        coz = math.sin(math.radians(dir)) * 0.5
        speedx = cox
        speedz = coz
        pygame.mixer.Channel(0).play(sound1)
        framelast = 1
        sframe = 1

        if playerx > bx - 6 :
            if playerx < bx + 6 :
                if playerz > bz - 6 :
                    if playerz < bz + 6 :
                        if playery > by - 6:
                            if playery < by + 6 :
                                impact_last = 3
                                impact = 3
                                if playerx > bx - 32 * lol:
                                    if playerx < bx + 32 * lol:
                                        if playerz > bz - 32 * lol:
                                            if playerz < bz + 32 * lol:
                                                if playery > by - 32 * lol:
                                                    if playery < by + 32 * lol:
                                                        pygame.mixer.Channel(0).play(b4)
                                                        if playerx > bx - 25.6 * lol:
                                                            if playerx < bx + 25.6 * lol:
                                                                if playerz > bz - 25.6 * lol:
                                                                    if playerz < bz + 25.6 * lol:
                                                                        if playery > by - 25.6 * lol:
                                                                            if playery < by + 25.6 * lol:
                                                                                pygame.mixer.Channel(0).play(b3)
                                                                                if playerx > bx - 19.2 * lol:
                                                                                    if playerx < bx + 19.2 * lol:
                                                                                        if playerz > bz - 19.2 * lol:
                                                                                            if playerz < bz + 19.2 * lol:
                                                                                                if playery > by - 19.2 * lol:
                                                                                                    if playery < by + 19.2 * lol:
                                                                                                        pygame.mixer.Channel(0).play(b2)
                                                                                                        if playerx > bx - 12.8 * lol:
                                                                                                            if playerx < bx + 12.8 * lol:
                                                                                                                if playerz > bz - 12.8 * lol:
                                                                                                                    if playerz < bz + 12.8 * lol:
                                                                                                                        if playery > by - 12.8 * lol:
                                                                                                                            if playery < by + 12.8 * lol:
                                                                                                                                pygame.mixer.Channel(0).play(b1)
                        pygame.mixer.Channel(2).play(sound3)
                        bsx = xx * 0.5
                        bsz = zz * 0.5
                        bsy = 0.3
    else:
        e = 0

    #animated objs
    s = 's'
    result = s + str(round(sframe%6))
    s = 'f'
    tree_sprite = s + str(round(tree_frame % 9))


    sframe +=0.5
    if keyboard.is_pressed("d"):
        spex+=0.0025
    if keyboard.is_pressed("a"):
        spex-=0.0025
    spex+=0-spex * 0.005
    speedxxxx = math.sin(math.radians(spex)) * 2
    spex+=0
    camyy -=0.25
    if camyy < 0:
        camyy = 0
    press-=1
    gbt+=0.1
    whaid-=0.1
    if gb == -1:
        xx = math.sin(math.radians(ball.rotation_y+90)) * 2
        zz = math.cos(math.radians(ball.rotation_y+90)) * 2
        bdx = playerx - bx +xx
        bdy = playery - by + math.sin(math.radians(anim+0.08)) * 0.16
        bdz = playerz - bz +zz
        bx+=bdx*0.75
        by+=bdy*0.75
        bz+=bdz*0.75
        bsy=speed_y /7.5
        bsx=speedx*2
        bsz=speedz*2
        ball.rotation_y=obj.rotation_y
        ball.shad.rotation_y = obj.rotation_y
    else:
     if impact < 0:
      bsy-=0.25/20
      by+=bsy
      bsx = bsx * 0.99
      bsz = bsz * 0.99
      bx += bsx
      bz += bsz
      playerx += speedx * time.dt * 50 / 2
      playerz += speedz * time.dt * 50 / 2
    speed = math.sqrt(speedx ** 2 + speedz ** 2)
    dx=math.sin(math.radians(dir_y)) * speed * 50
    dy = speed * 10
    dz=math.cos(math.radians(dir_y)) * speed * -50
    camx = playerx  + spex + math.sin(math.radians(dir_y)) * zoom
    camy = playery  + 6 + math.cos(math.radians(TICK / 2)) * 1 + yy
    camz = playerz  + math.cos(math.radians(dir_y)) * zoom * -1
    camx+= math.sin(math.radians(dir_y)) * speed * 50  *0.2
    camy+= speed * 10 * 0.2
    camz+= math.cos(math.radians(dir_y)) * speed * -50  *0.2 + 20
    if impact_last < 0:
       playery += speed_y /15
    frame += speed /  10
    if not sf == 0:
        dir += 22.5/2
        sf +=1
        cox = math.cos(math.radians(dir)) * 0.1
        coz = math.sin(math.radians(dir)) * 0.1
        speedx = cox
        speedz = coz
        if sf == 16:
            sf = 0
            spin =0


    if keyboard.is_pressed("e") or joystick.get_button(3) == 1:
      if pressed == 0:
        spin = dir
        sf = 1
        pressed = 1
        cox = math.cos(math.radians(dir)) * 0.1
        coz = math.sin(math.radians(dir)) * 0.1
        speedx = cox
        speedz = coz
    else:
        pressed = 0

    if by<-2:
        if bsy < -0.2:
            if playerx > bx - 32* lol:
                if playerx < bx + 32* lol:
                    if playerz > bz - 32* lol:
                        if playerz < bz + 32* lol:
                            if playery > by - 32* lol:
                                if playery < by + 32* lol:
                                    pygame.mixer.Channel(0).play(b4)
                                    if playerx > bx - 25.6* lol:
                                        if playerx < bx + 25.6* lol:
                                            if playerz > bz - 25.6* lol:
                                                if playerz < bz + 25.6* lol:
                                                    if playery > by - 25.6* lol:
                                                        if playery < by + 25.6* lol:
                                                            pygame.mixer.Channel(0).play(b3)
                                                            if playerx > bx - 19.2* lol:
                                                                if playerx < bx + 19.2* lol:
                                                                    if playerz > bz - 19.2* lol:
                                                                        if playerz < bz + 19.2* lol:
                                                                            if playery > by - 19.2* lol:
                                                                                if playery < by + 19.2* lol:
                                                                                    pygame.mixer.Channel(0).play(b2)
                                                                                    if playerx > bx - 12.8* lol:
                                                                                        if playerx < bx + 12.8* lol:
                                                                                            if playerz > bz - 12.8* lol:
                                                                                                if playerz < bz + 12.8* lol:
                                                                                                    if playery > by - 12.8* lol:
                                                                                                        if playery < by + 12.8* lol:
                                                                                                            pygame.mixer.Channel(0).play(b1)
        by=-2
        bsy*=-0.9
    if round(frame / 2)  % 12 == 1:
        anim = 0
        pygame.mixer.Channel(3).play(sound3)
        frame = 0
    obj.y = playery - camy + math.sin(math.radians(anim)) * 0.08
    obj.scale = (1.5 - yyyy / 10 ,yyyy / 5 + 1.5 , 1.5 - yyyy / 10)
    obj.shad.y = playery - camy - 0.01  + math.sin(math.radians(anim)) * 0.08
    obj.shad.scale = (1.5 - yyyy / 10 ,yyyy / 5 + 1.5 , 1.5 - yyyy / 10)
    obj.z = playerz - camz
    obj.shad.z = playerz - camz-0.01
    obj.x = playerx - camx
    obj.shad.x = playerx - camx-0.01
    obj.reflect.y = 0- playery - camy-5-0.05- math.sin(math.radians(anim)) * 0.08
    obj.reflect.scale = (1.5 - yyyy / 10, yyyy / 5 + 1.5, 1.5 - yyyy / 10)
    obj.shad.ref.y = 0- playery - camy-5+0.05- math.sin(math.radians(anim)) * 0.08
    obj.shad.ref.scale = (1.5 - yyyy / 10, yyyy / 5 + 1.5, 1.5 - yyyy / 10)
    obj.reflect.z = playerz - camz
    obj.shad.ref.z = playerz - camz-0.01
    obj.reflect.x = playerx - camx
    obj.shad.ref.x = playerx - camx-0.01
    if editor == -1:
        obj.y = yyy - camy
        obj.shad.y = yyy - camy - 0.01
        obj.z = zzz - camz
        obj.shad.z = zzz - camz - 0.01
        obj.x = xxx - camx
        obj.shad.x = xxx - camx - 0.01
        obj.reflect.y = 0 - yyy - camy - 5
        obj.shad.ref.y = 0 - yyy - camy - 5 + 0.01
        obj.reflect.z = zzz - camz
        obj.shad.ref.z = zzz - camz - 0.01
        obj.reflect.x = xxx - camx
        obj.shad.ref.x = xxx - camx - 0.01
    block.y = -3 - camy
    block.z = 0 - camz
    block.x = 0 - camx
    ball.y = by - camy
    ball.shad.y = by - camy-0.02
    ball.z = bz - camz
    ball.shad.z = bz - camz-0.02
    ball.x = bx - camx
    ball.shad.x = bx - camx-0.02
    ball.ref.y = 0- by - camy-5
    ball.ref.shad.y = 0- by - camy-5+0.02
    ball.ref.z =  bz - camz
    ball.ref.shad.z = bz - camz-0.02
    ball.ref.shad.x = bx-camx-0.02
    ball.ref.x = bx-camx
    ball.ref.rotation_y=ball.rotation_y
    if speedx != 0 or speedz != 0:
        angle = math.atan2(speedz, speedx)
        dir = math.degrees(angle)
        if slow == 1 :
            obj.rotation = (0, round(-dir  / 16) * 16, round (speed*40 /8)*8 + round (roll / 35) * 35)  # turn left/right based on movement
            obj.shad.rotation = (0,round(-dir  / 16) * 16, round (speed *40 / 8) *8 + round (roll / 35) * 35)  # turn left/right based on movement
            obj.reflect.rotation = (0, obj.rotation_y, round(speed * -40 / 8) * 8 + round(roll / 35) * -35)  # turn left/right based on movement
            obj.shad.ref.rotation = (0, obj.rotation_y, round(speed * -40 / 8) * 8 + round(roll / 35) * -35)  # turn left/right based on movement
        else:
            obj.rotation = (0, round(-dir  / 16) * 16,round(speed * 40 / 8) * 16 + round(roll / 35) * 70)  # turn left/right based on movement
            obj.shad.rotation = (0, round(-dir  / 16) * 16,round(speed * 40 / 8) * 16 + round(roll / 35) * 70)  # turn left/right based on movement
            obj.reflect.rotation = (0, obj.rotation_y, round(speed * -40 / 8) * 16 + round(roll / 35) * -70)  # turn left/right based on movement
            obj.shad.ref.rotation = (0, obj.rotation_y , round(speed * -40 / 8) * 16 + round(roll / 35) * -70)  # turn left/right based on movement
    if keyboard.is_pressed('shift') or joystick.get_button(4) == 1:
         if playerx > bx-6:
            if playerx < bx+6:
                if playerz > bz-6:
                    if playerz < bz+6:
                        if playery > by-6:
                            if playery < by+6:
                              if gbt > 2:
                                gbt = 0
                                gb=gb*-1
    if frame > 12:
         frame = 0

    pdir = dir
    message.text= str('X : ') + str (playerx)
    messag1.text=str('Y : ') + str (playery)
    messag2.text=str('Z : ') + str (dob_tim)
    messag3.text=str('DIRECTION : ') + str(round(obj.rotation_y/2)*2)
    messag4.text=str('TICK : ') + str (wallrunz)
    camera.look_at(obj)
    camera.rotation_z = 0  # Tilt downward
    camera.rotation_y = dir_y * -1  # Follow player’s Y rotation
    bhad.x = -10.3 - camx
    bhad.y = -0 - camy
    bhad.z = 0 - camz



    bhad.rotation_x =90
    bhad.rotation_y = 90
    bhad.rotation_z = -90
    tshad.x = -10.3- camx
    tshad.y = -2.2 - camy
    tshad.z = -2 - camz
    tshad. rotation_x =180
    tshad.rotation_y = 180

    if keyboard.is_pressed('0'):
      if whaid < 0:
        debug*= -1
        whaid=2
    if debug == -1:
        speed_y = 0
        dir_y = 0
        if keyboard.is_pressed('w'):
            playerz+=0.05
        if keyboard.is_pressed('s'):
            playerz-= 0.05
        if keyboard.is_pressed('a'):
            playerx -= 0.05
        if keyboard.is_pressed('d'):
            playerx +=0.05
        if keyboard.is_pressed('y'):
            playery-= 0.05
        if keyboard.is_pressed('u'):
            playery+= 0.05
        if keyboard.is_pressed('l'):
          if lp == 0 :
            lp = 1
            # Store cube data
            block_info.append(round(playerx / 1.5) * 1.5)
            block_info.append(round(playery / 1.5) * 1.5)
            block_info.append(round(playerz / 1.5) * 1.5)
            block_info.append(1)  # maybe block type
            i = 0
            while i < 50 :
                print(     )
                i += 1
            print (block_info)

            # Create cube entity from last 4 values
            start = len(block_info) - 4
            x, y, z, block_type = block_info[start:start + 4]

            cube_name = f"cube{start // 4}"
            cubes[cube_name] = Entity(
                model='cube',
                position=(x, y, z),
                scale=(1.5, 1.5, 1.5),
                rotation=(0, 0, 0),
                texture='tex.png',
                color=color.rgb(50, 50, 70))

            start = len(block_info) - 4
            x, y, z, block_type = block_info[start:start + 4]

            cube_name = f"cube{start // 4}"
            cs[cube_name] = Entity(
                model='cube',
                position=(x, y, z),
                scale=(1.5, 1.5, 1.5),
                rotation=(0, 0, 0),
                texture='tex.png',
                color=color.rgb(50, 50, 70))
        else:
            lp = 0

    xx = math.sin(math.radians(obj.rotation_y+90)) * 2
    zz=math.cos(math.radians(obj.rotation_y+90)) * 2
    block2.x= playerx - camx+xx
    block2.y= playery - camy
    block2.z = playerz - camz+zz
    block2.rotation_y=obj.rotation_y
    bshad.x = playerx - camx
    bshad.y = -2.5-camy
    bshad.z = playerz - camz
    bshad.rotation_y= obj.rotation_y
    bsshad.y = -2.5 - camy
    bsshad.z = bz - camz
    bsshad.x = bx - camx
    bhad.texture=tree_sprite
    bhad.rotation_y = dir_y * -1
    bhad.rotation_y += 90

    if sframe > 5:
        sframe=5
        framelast = 0
    if framelast> 0 :
        block2.texture=result
    else:
        block2.texture = 's5.png'
    if keyboard.is_pressed('r'):
        speed_y = 0
        playery = 0
        speedx = 0
        speedz = 0
        playerx = 0
        playerz = 0
        decellx = 0
        decellz = 0
        camx = 0
        camy = 0
        camz = 0
        dx = 0
        dy = 0
        dz = 0
        bx = 0
        by = 10
        bz = 0
        bsx = 0
        bsy = 0
        bsz = 0
        frame = 0
        speed = 0
        gb = 1
        gbt = 0
        bdx = 0
        bdy = 0
        bdz = 0
        press = 0
        cox = 0
        coz = 0
        utg = 0
        xx = 0
        zz = 0
        debug = 1
        whaid = 0
        camyy = 40
        speedxxxx = 0
        spex = 0
        result = 0
        s = 's'
        framelast = 0
        sframe = 5
        dir = 9


    editor=1
    if keyboard.is_pressed('9'):
         editor = -1
         xxx = round (playerx /1.5) * 1.5
         yyy = round (playery /1.5) * 1.5
         zzz = round (playerz/1.5) * 1.5

    i = 0
    while i < len(block_info) / 4:
        index = int(i * 4)
        cubes['cube' + str(i)].x = block_info[index] - camx
        cubes['cube' + str(i)].y = block_info[index + 1] - camy-1.5
        cubes['cube' + str(i)].z = block_info[index + 2] - camz
        i += 1

    i = 0
    while i < len(block_info) / 4:
        index = int(i * 4)

        cs['cube' + str(i)].x = block_info[index] - camx - 0.01
        cs['cube' + str(i)].y = block_info[index + 1] - camy - 1.5-0.01
        cs['cube' + str(i)].z = block_info[index + 2] - camz -0.01
        i += 1


    i = 0
    for i in range(0, len(block_info) - 2, 4):
        colx = block_info[i]
        coly = block_info[i + 1]
        colz = block_info[i + 2]
        if colx + 3 > bx:
            if colx - 3 < bx:
                if colz + 3 > bz:
                    if colz - 3 < bz:
                        if coly - 3 < by:
                            if coly + 3 > by:
                                b_coli()
    light1 += 0.01
    light_1.x = 12 - camx
    light_1.y = 7.5 - camy
    light_1.z = -4 - camz

    enemy.x = ex - camx
    enemy.y = ey - camy
    enemy.z = ez - camz


    clock.tick(30)
    cube.x = 1000
    message1.x = 1000
    message2.x = 1000
    message3.x = 1000
    message4.x = 1000
    message5.x = 1000
    m6.x = 1000
    m66.x = 1000
    m1.x = 1000
    m2.x = 1000
    m4.x = 1000

    obj.texture = "tex.png"
    obj.shad.texture = "texs.png"
    obj.reflect.texture = "tex.png"
    obj.shad.ref.texture = "texs.png"

    ball.texture = "tex.png"
    ball.ref.texture = "texs.png"
    ball.shad.texture = "texs.png"
    ball.ref.shad.texture = "texs.png"

    bsshad.texture = "costume1 (1).png"

    block.texture = "texs2.png"
    enemy.texture = "tex2.png"

    if slow == -1:
        obj.texture = "tex(s).png"
        obj.shad.texture = "texs(s).png"
        obj.reflect.texture = "tex(s).png"
        obj.shad.ref.texture = "texs(s).png"

        ball.texture = "tex(s).png"
        ball.shad.texture = "texs(s).png"
        ball.ref.texture = "texs(s).png"
        ball.ref.shad.texture = "texs(s).png"

        bsshad.texture = "costume2 (1)(s).png"
        block.texture = "texs3(s).png"

        enemy.texture = "tex2 (1).png"


app = Ursina()
#entities
obj = Entity(model='cube', position=(0,0,0), scale=(1.5), rotation=(0,0,0,), texture= 'tex.png', color = color.rgb(50,50,70),)
obj.shad = Entity(model='cube', position=(0,0,0), scale=(1.5), rotation=(0,0,0,), texture= 'texs.png', color = color.rgb(50,50,70),)
obj.reflect = Entity(model='cube', position=(0,0,0), scale=(1.5), rotation=(0,0,0,), texture= 'tex.png', color = color.rgb(50,50,70),)
obj.shad.ref = Entity(model='cube', position=(0,0,0), scale=(1.5), rotation=(0,0,0,), texture= 'texs.png', color = color.rgb(50,50,70),)
block = Entity(model='cube', position=(0,-3,0), scale=(1000,1.5,1000), rotation=(0,0,0,), texture= 'texs2.png', color = color.rgb(50,50,70),)
enemy = Entity(model='cube', position=(0,0,0), scale=(1.5), rotation=(0,0,0,), texture= 'tex2.png', color = color.rgb(50,255,70),)

message = Text(text='', scale=1, color=color.white, position=(-0.6,0.4))
messag1 = Text(text='', scale=1, color=color.white, position=(-0.6,0.35))
messag2 = Text(text='', scale=1, color=color.white, position=(-0.6,0.3))
messag3 = Text(text='', scale=1, color=color.white, position=(-0.6,0.25))
messag4 = Text(text='', scale=1, color=color.white, position=(-0.6,0.2))
ball = Entity(model='cube',scale=(1.5),texture='tex.png',)
ball.shad = Entity(model='cube',scale=(1.5),texture='texs.png',)
ball.ref = Entity(model='cube',scale=(1.5,1.5,1.5), rotation=(0,0,0,),texture='tex.png',)
ball.ref.shad = Entity(model='cube',scale=(1.5,1.5,1.5), rotation=(0,0,0,),texture='texs.png',)
window.fullscreen = True
mouse.locked = True
window.color = color.rgb(0.5,0.5,0.7)
block2 = Entity(model='cube', position=(0,5,0), scale=(5,0.001,5), rotation=(0,0,0,), texture= 's1.png', color = color.rgb(50,50,70),)
light_1 = Entity(model='cube', position=(0,5,0), scale=(26,0.001,20), rotation=(90,90,90,), texture= 'light.png', color = color.rgb(50,50,70),)
bshad = Entity(model='cube', position=(0,5,0), scale=(2,0.001,2), rotation=(0,0,0,), texture= 'costume1 (2).png', color = color.rgb(50,50,70),)
bsshad = Entity(model='cube', position=(0,5,0), scale=(1.5,0.001,1.5), rotation=(0,0,0,), texture= 'costume1 (1).png', color = color.rgb(50,50,70),)
bhad = Entity(model='cube', position=(0,5,0), scale=(4,0.001,5.4), rotation=(0,0,0,), texture= 'f1', color = color.rgb(50,50,70),)
tshad = Entity(model='cube', position=(0,5,0), scale=(4,0.001,4), rotation=(0,0,0,), texture= 'download (1) (1) (1).png', color = color.rgb(50,50,70),)

message1 = Text(text='', scale=1.5, color=color.white, position=(-0.8,0.35))
message2 = Text(text='', scale=1.5, color=color.white, position=(-0.8,0.3))
message3 = Text(text='', scale=1.5, color=color.white, position=(-0.805,0.25))
message4 = Text(text='', scale=1.5, color=color.white, position=(-0.45,0.2))
message5 = Text(text='', scale=1.5, color=color.white, position=(-0.6,0.15))
m6 = Text(text='Hello, Ursina!', scale=1.5, color=color.white, position=(-0.5,0.15))
m1 = Text(text='Hello, Ursina!', scale=1.5, color=color.white, position=(-0,0.15))
m2 = Text(text='Hello, Ursina!', scale=1.5, color=color.white, position=(-0.1,0.15))
m4 = Text(text='Hello, Ursina!', scale=1.5, color=color.white, position=(-0.4,0.15))
m66 = Text(text='Hello, Ursina!', scale=1.5, color=color.white, position=(-0.35,0.15))
cube = Entity(model='cube',texture = "costume1 (6).png" ,color=color.black,position=(0,0,0,), scale=(90/2,50/2,0))
window.fullscreen = True
camera.bg_color = color.black

message1.text = "Theo stormblade comes from the mystical land of elementia where all the elemental forces lived "
m1.text = "lived ."
message2.text = "stormblade had the rare ability to control all the elemental forces by learning from a warrior "
m2.text =  "from a very young age"
message3.text = "he had learned how to control all the elemental forces he was a warrior later in his life when"
message4.text = "he was told by the citizens of elementia that a dark force"
m4.text =  " threatend them to come to their land to fight them"
message5.text = "or that they will destroy elementia where all the elemental forces lived."
m6.text = "Our hero started his journey to the dark force battlefield"
m66.text = "risking his life for the land of elementia......."

app.run()