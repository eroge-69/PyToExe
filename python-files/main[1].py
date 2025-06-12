from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()

# HD-Texturen laden
grass_tex = load_texture('assets/grass.png')
stone_tex = load_texture('assets/stone.png')
brick_tex = load_texture('assets/brick.png')
dirt_tex  = load_texture('assets/dirt.png')

textures = [grass_tex, stone_tex, brick_tex, dirt_tex]
block_pick = 0

def update():
    global block_pick
    if held_keys['left mouse'] or held_keys['right mouse']:
        hand.rotation_x = 30
    else:
        hand.rotation_x = 0

    for i in range(4):
        if held_keys[str(i + 1)]:
            block_pick = i

class Voxel(Button):
    def __init__(self, position=(0,0,0), texture=grass_tex):
        super().__init__(
            parent=scene,
            position=position,
            model='cube',
            origin_y=0.5,
            texture=texture,
            color=color.white,
            scale=0.5
        )

    def input(self, key):
        if self.hovered:
            if key == 'left mouse down':
                destroy(self)
            if key == 'right mouse down':
                Voxel(position=self.position + mouse.normal, texture=textures[block_pick])

# Welt generieren
for z in range(16):
    for x in range(16):
        Voxel(position=(x,0,z), texture=grass_tex)

# Spieler
player = FirstPersonController()
player.gravity = 0.3
player.cursor.visible = True

# Hand
hand = Entity(
    parent=camera.ui,
    model='cube',
    texture=grass_tex,
    scale=(0.2, 0.4),
    color=color.white,
    rotation=Vec3(150, -10, 0),
    position=Vec2(0.5, -0.6)
)

Sky()
app.run()
