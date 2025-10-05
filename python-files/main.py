from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random

score=0
ammo=12
health=100
inviata=1

def pozitie():
    global a, b, c
    a=random.randint(-40, 40)
    b=0.6
    c=random.randint(-40, 40)

def culoare():
    global R, G, B
    R=random.randint(0, 255)
    G=random.randint(0, 255)
    B=random.randint(0, 255)

app=Ursina()

Sky()

for z in range(2):
    for x in range(2):
        Entity(model="cube", scale=(100, 1, 100), texture="podea.png", parent=scene, collider="box", ignore=False)
perete1=Entity(model="cube", scale=(100, 10, 1), position=(0, 5.5, 50), collider="box", texture="perete.png")
perete2=Entity(model="cube", scale=(100, 10, 1), position=(0, 5.5, -50), collider="box", texture="perete.png")
perete3=Entity(model="cube", scale=(100, 10, 1), position=(50, 5.5, 0), collider="box", texture="perete.png")
perete3.rotation_y=90
perete4=Entity(model="cube", scale=(100, 10, 1), position=(-50, 5.5, 0), collider="box", texture="perete.png")
perete4.rotation_y=90

audio1=Audio("sunet.mp3", autoplay=False, loop=False)
reload2=Audio("reload.mp3", autoplay=False, loop=False)
punch3=Audio("punch.mp3", autoplay=False, loop=False)
fundal4=Audio("fundal.mp3", autoplay=True, loop=True)

player=FirstPersonController(model="shotgun 1.glb", scale=(2, 2.5, 2))
player.gravity=0
player.y=0
player.x=-0.2
camera.x=0
camera.y=-1
camera.z=-1

bullet=None

pause=Text(text="Pause (press 'o' to resume)", x=-0.4, y=0.3, scale=3, visible=False)

def aux():
    player.rotation_x=0

def input(key):
    global bullet, ammo, score, cube, cube2, audio1, health, inviata, aux
    if ammo>0:
        if key == 'left mouse up':
            ammo-=1
            bullet = Entity(parent=player, model="cube", scale=(0.1, 0.1, 0.3), color=color.red, collider='box', position=(0, 1.2, 0))
            bullet.world_parent = scene
            bullet.animate_position(bullet.position+bullet.forward*1000, duration=0.5)
            audio1.play()
    if key == 'right mouse up':
        if distance(player, cube)<10:
            cube.z=cube.z-5
            punch3.play()
        if distance(player, cube2)<10:
            cube2.z=cube2.z-5
            punch3.play()
    if key == 'b up' and ammo<=60:
        score-=3
        ammo+=12
        reload2.play()
        player.rotation_x=-20
        invoke(aux, delay=0.6)
        
    if key == 'h up' and health<=150:
        score-=1
        health+=25
    if key=='p up':
        player.enabled=False
        pause.visible=True
        cube.enabled=False
        cube2.enabled=False
        cube.visible=False
        cube2.visible=False
    if key=='o up':
        player.enabled=True
        pause.visible=False
        cube.enabled=True
        cube2.enabled=True
        cube.visible=True
        cube2.visible=True
    if key=='space up' and inviata==0:
        inviata=1
        player.rotation_x=0
        player.x=0
        player.z=0
        score=0
        ammo=12
        health=100
        cube.enabled=True
        cube2.enabled=True
        cube.visible=True
        cube2.visible=True
        update()

cube=None
cube2=None
def cub1():
    global cube
    pozitie()
    culoare()
    cube=Entity(model="om.glb", scale=(4, 4, 4), collider='box', position=(a, b, c), color=rgb(R, G, B))
    
def cub2():
    global cube2
    pozitie()
    culoare()
    cube2=Entity(model="om.glb", scale=(4, 4, 4), collider='box', position=(a, b, c), color=rgb(R, G, B))

warn=Text(text="Buy Ammo NOW! (press 'b' to buy)", x=-0.6, y=0, scale=3, visible=False)
dead=Text(text="You're dead! (press 'space' to restart)", x=-0.7, y=0, scale=3, color=color.red, visible=False)

cub1()
cub2()

texte=Text(text=("Score: " + str(score)), x=-0.73, y=-0.45)
magazie=Text(text=("Ammo: " + str(ammo)), x=0.57, y=-0.45)
viata=Text(text=("Health: " + str(health)), x=0, y=-0.45)

def update():
    global cube, cube2, bullet, score, ammo, warn, health, dead, inviata
    texte.text=("Score: " + str(score))
    magazie.text=("Ammo: " + str(ammo))
    viata.text=("Health:" + str(health))

    if cube.enabled==True:
        cube.look_at(player)
        cube.animate_position(cube.position+cube.forward*70, duration=5)

    if cube2.enabled==True:
        cube2.look_at(player)
        cube2.animate_position(cube2.position+cube2.forward*70, duration=5)

    if health<=0:
        dead.visible=True
        player.rotation_x=90
        cube.enabled=False
        cube2.enabled=False
        cube.visible=False
        cube2.visible=False
        inviata=0
        return
    else:
        dead.visible=False

    if distance(player, cube)<=2:
        health-=0.5

    if distance(player, cube2)<=2:
        health-=0.5

    if bullet and bullet.intersects(cube):
        destroy(bullet)
        destroy(cube)
        cub1()
        if distance(player, cube)>40:
            score+=2
        else:
            score+=1

    if bullet and bullet.intersects(cube2):
        destroy(bullet)
        destroy(cube2)
        cub2()
        if distance(player, cube2)>40:
            score+=3
        else:
            score+=2

    if bullet and bullet.intersects(perete1).hit:
        score-=1
    if bullet and bullet.intersects(perete2).hit:
        score-=1
    if bullet and bullet.intersects(perete3).hit:
        score-=1
    if bullet and bullet.intersects(perete4).hit:
        score-=1
    if ammo<=0:
        warn.visible=True
    else:
        warn.visible=False
    
app.run() 