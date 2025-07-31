from ursina import *

app = Ursina()

player = Entity(model='cube', color=color.orange, scale_y=2, collider='box')
ground = Entity(model='plane', scale=64, texture='grass', collider='box')

camera.position = (0, 10, -30)
camera.rotation_x = 30

def update():
    if held_keys['a']: player.x -= 0.1
    if held_keys['d']: player.x += 0.1
    if held_keys['s']: player.z -= 0.1
    if held_keys['w']: player.z += 0.1

app.run()
