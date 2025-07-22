from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
app = Ursina()
texture = load_texture('block.jpg')
texturepavimento = load_texture('grass.jpg')
block = Entity(model='cube', texture=texture, position=(0, -9,999, 0), scale=(1, 1, 1), collider='box')
block.texture.filtering = False
block.texture.alpha = 1
player = FirstPersonController()
player.scale = (0.9, 0.9, 0.9)
player.jump_height = 1.5
player.gravity = 0.5
player.fall_after = 0.2
player.drag = 0.05
player.air_time = 0
for x in range(-20, 20):
    for z in range(-20, 20):
        Entity(
            model='cube',
            texture=texturepavimento,
            position=(x, -10, z),
            scale=(1, 1, 1),
            collider='box'
        )

sky = Sky()
sky.color = color.rgb(135, 206, 235)

from ursina import mouse, Text, distance

barriere = []
for x in range(-21, 22):
    barriere.append(Entity(model='cube', color=color.rgba(255,255,255,0), position=(x, 40, -21), scale=(1, 100, 1), collider='box'))
    barriere.append(Entity(model='cube', color=color.rgba(255,255,255,0), position=(x, 40, 20), scale=(1, 100, 1), collider='box'))
for z in range(-21, 22):
    barriere.append(Entity(model='cube', color=color.rgba(255,255,255,0), position=(-21, 40, z), scale=(1, 100, 1), collider='box'))
    barriere.append(Entity(model='cube', color=color.rgba(255,255,255,0), position=(20, 40, z), scale=(1, 100, 1), collider='box'))
soffitto = Entity(model='cube', color=color.rgba(255,255,255,0), position=(0, 41, 0), scale=(42, 1, 42), collider='box')
from ursina import mouse, Text
pausa_label = Text('PAUSA', origin=(0,0), scale=3, enabled=False)
in_pausa = [False]


from ursina import Text
mirino = Entity(
    parent=camera.ui,
    model='quad',
    color=color.black,
    scale=(0.0125, 0.0125),
    position=(0,0,0)
)
hovered_last = [None]

def input(key):
    if key == 'escape':
        in_pausa[0] = not in_pausa[0]
        mouse.locked = not in_pausa[0]
        pausa_label.enabled = in_pausa[0]

    max_reach = 9
    if key == 'left mouse down' and mouse.hovered_entity:
        if mouse.hovered_entity != player and mouse.hovered_entity != pausa_label:
            if (not hasattr(mouse.hovered_entity, 'texture') or mouse.hovered_entity.texture != texturepavimento) and distance(player.position, mouse.hovered_entity.position) <= max_reach:
                destroy(mouse.hovered_entity)
    if key == 'right mouse down' and mouse.hovered_entity:
        pos = mouse.hovered_entity.position + mouse.normal
        if distance(player.position, pos) <= max_reach:
            Entity(
                model='cube',
                texture=texture,
                position=pos,
                scale=(1, 1, 1),
                collider='box'
            )

def update():
    barriere_set = set(barriere + [soffitto])
    max_reach = 9
    if (
        mouse.hovered_entity and
        hasattr(mouse.hovered_entity, 'color') and
        hasattr(mouse.hovered_entity, 'collider') and
        mouse.hovered_entity not in barriere_set and
        distance(player.position, mouse.hovered_entity.position) <= max_reach
    ):
        if hovered_last[0] and hovered_last[0] != mouse.hovered_entity:
            hovered_last[0].color = color.white
        mouse.hovered_entity.color = color.red
        hovered_last[0] = mouse.hovered_entity
    elif hovered_last[0]:
        hovered_last[0].color = color.white
        hovered_last[0] = None

app.run()