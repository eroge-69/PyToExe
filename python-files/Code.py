from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random

app = Ursina()

# Create the player without the default capsule model visible
player = FirstPersonController()
player.gravity = 1
player.cursor.visible = False  # Hide default cursor for our custom crosshair
player.model = None  # Hide default model

# Steve avatar parts
class Steve(Entity):
    def __init__(self, parent):
        super().__init__(parent=parent)
        # Head (8x8x8), scale down to Ursina scale
        self.head = Entity(parent=self, model='cube', scale=(0.5,0.5,0.5), position=(0,1.5,0), texture='steve_head.png')
        # Body (8x12x4)
        self.body = Entity(parent=self, model='cube', scale=(0.5,0.75,0.25), position=(0,0.75,0), texture='steve_body.png')
        # Left Arm
        self.left_arm = Entity(parent=self, model='cube', scale=(0.2,0.75,0.25), position=(-0.4,0.75,0), texture='steve_arm.png')
        # Right Arm
        self.right_arm = Entity(parent=self, model='cube', scale=(0.2,0.75,0.25), position=(0.4,0.75,0), texture='steve_arm.png')
        # Left Leg
        self.left_leg = Entity(parent=self, model='cube', scale=(0.2,0.75,0.25), position=(-0.15,0,0), texture='steve_leg.png')
        # Right Leg
        self.right_leg = Entity(parent=self, model='cube', scale=(0.2,0.75,0.25), position=(0.15,0,0), texture='steve_leg.png')

# Load Steve textures - fallback to colors if textures missing
try:
    steve = Steve(parent=player)
except Exception as e:
    print("Steve textures missing! Using colors instead.")
    steve = Steve(parent=player)
    steve.head.texture = None
    steve.head.color = color.azure
    steve.body.texture = None
    steve.body.color = color.blue
    steve.left_arm.texture = None
    steve.left_arm.color = color.orange
    steve.right_arm.texture = None
    steve.right_arm.color = color.orange
    steve.left_leg.texture = None
    steve.left_leg.color = color.brown
    steve.right_leg.texture = None
    steve.right_leg.color = color.brown

Sky()

# ----------- CLOUDS -------------

cloud_texture = 'cloud.png'  # You need to have this transparent cloud texture in your folder

class Cloud(Entity):
    def __init__(self, position, speed):
        super().__init__(
            parent=scene,
            model='quad',
            texture=cloud_texture,
            scale=(10,5),
            position=position,
            billboard=True,
            color=color.rgba(255, 255, 255, 150),  # semi-transparent clouds
            double_sided=True
        )
        self.speed = speed

    def update(self):
        self.x += self.speed * time.dt
        if self.x > 40:
            self.x = -10

clouds = []
for i in range(7):
    c = Cloud(position=Vec3(random.uniform(-10, 30), random.uniform(10, 15), random.uniform(-10, 30)),
              speed=random.uniform(0.5, 1.5))
    clouds.append(c)

# ------------------------------

# Add a small red dot crosshair
crosshair_dot = Entity(
    parent=camera.ui,
    model='circle',
    scale=0.008,
    color=color.red,
    position=Vec2(0, 0)
)

# Perspective toggle state: 0=first-person, 1=third-person back, 2=third-person front
perspective_mode = 0

# Block types with textures and display names
block_types = [
    {'name': 'Grass', 'texture': 'grass.png'},
    {'name': 'Wood', 'texture': 'wood.png'},
    {'name': 'Stone', 'texture': 'stone.png'},
]

current_block_index = 0

boxes = []

# Create ground blocks
for i in range(35):
    for j in range(35):
        block = Button(color=color.white, model='cube', position=(j, 0, i),
                       texture='grass.png', parent=scene, origin_y=0.5)
        boxes.append(block)

# Simple hotbar UI buttons at bottom center
hotbar_buttons = []
hotbar_y = -0.4
for i, block in enumerate(block_types):
    btn = Button(
        parent=camera.ui,
        model='cube',
        texture=block['texture'],
        color=color.white,
        scale=0.1,
        position=Vec3(-0.3 + i * 0.15, hotbar_y, 0),
    )
    hotbar_buttons.append(btn)

def update_hotbar():
    for i, btn in enumerate(hotbar_buttons):
        btn.color = color.azure if i == current_block_index else color.white

update_hotbar()

# NPC villager class
class Villager(Entity):
    def __init__(self, position=(0,1,0), **kwargs):
        super().__init__(
            model='cube',
            color=color.orange,
            scale=(0.5,1,0.5),
            position=position,
            **kwargs
        )
        self.direction = Vec3(random.uniform(-1,1), 0, random.uniform(-1,1)).normalized()
        self.speed = 1

    def update(self):
        self.position += self.direction * self.speed * time.dt
        if not (0 < self.position.x < 34):
            self.direction.x *= -1
        if not (0 < self.position.z < 34):
            self.direction.z *= -1

# Spawn a few villagers
villagers = [Villager(position=(random.uniform(5,30),1,random.uniform(5,30))) for _ in range(5)]

fly_mode = False

def update():
    global fly_mode

    # Update NPCs
    for v in villagers:
        v.update()

    # Update clouds
    for c in clouds:
        c.update()

    # Fly mode toggle movement
    if fly_mode:
        player.gravity = 0
        speed = 5 * time.dt
        if held_keys['space']:
            player.position += Vec3(0, speed, 0)
        if held_keys['shift']:
            player.position -= Vec3(0, speed, 0)
    else:
        player.gravity = 1

    # Sprint and crouch logic
    if held_keys['w']:
        if held_keys['control']:
            player.speed = 12
            player.camera_pivot.y = 1
        elif held_keys['shift']:
            player.speed = 3
            player.camera_pivot.y = 0.5
        else:
            player.speed = 6
            player.camera_pivot.y = 1
    else:
        player.speed = 6
        player.camera_pivot.y = 1

    # Hide Steve’s head and arms in first person
    if perspective_mode == 0:
        steve.head.enabled = False
        steve.left_arm.enabled = False
        steve.right_arm.enabled = False
    else:
        steve.head.enabled = True
        steve.left_arm.enabled = True
        steve.right_arm.enabled = True

def input(key):
    global fly_mode, current_block_index, perspective_mode

    if key == 'f':
        fly_mode = not fly_mode
        print('Fly mode:', 'ON' if fly_mode else 'OFF')

    if key == 'p':
        perspective_mode = (perspective_mode + 1) % 3
        if perspective_mode == 0:
            camera.parent = player.camera_pivot
            camera.position = (0, 0, 0)
            camera.rotation = (0, 0, 0)
            player.cursor.visible = False  # Hide default cursor; using red dot
            print("Perspective: First Person")
        elif perspective_mode == 1:
            camera.parent = player
            camera.position = Vec3(0, 2, -5)
            camera.look_at(player.position + Vec3(0, 1, 0))
            player.cursor.visible = False
            print("Perspective: Third Person Back")
        elif perspective_mode == 2:
            camera.parent = player
            camera.position = Vec3(0, 2, 5)
            camera.look_at(player.position + Vec3(0, 1, 0))
            player.cursor.visible = False
            print("Perspective: Third Person Front")

    # Hotbar selection by clicking UI buttons
    for i, btn in enumerate(hotbar_buttons):
        if btn.hovered and key == 'left mouse down':
            current_block_index = i
            update_hotbar()
            print(f'Selected block: {block_types[current_block_index]["name"]}')

    # Place/remove blocks with mouse over world blocks
    for block in boxes:
        if block.hovered:
            if key == 'left mouse down':
                new_pos = block.position + mouse.normal
                if distance(new_pos, player.position) > 1.5:
                    new_block = Button(color=color.white, model='cube', position=new_pos,
                                       texture=block_types[current_block_index]['texture'], parent=scene, origin_y=0.5)
                    boxes.append(new_block)
            if key == 'right mouse down':
                if block.position.y > 0:
                    boxes.remove(block)
                    destroy(block)

app.run()
