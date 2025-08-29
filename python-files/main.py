from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from perlin_noise import PerlinNoise
import random

app = Ursina(title="Riscraft 1.1.0")
window.borderless = False
mouse.visible = False

# Настройки
SEED = random.randint(0, 9999)
CHUNK_SIZE = 16
WORLD_SIZE = 2
TEXTURES = {
    'grass': 'textures/block/grass.png',
    'dirt': 'textures/block/dirt.png',
    'stone': 'textures/block/stone.png',
    'bedrock': 'textures/block/bedrock.png'
}

class Voxel(Button):
    def __init__(self, position, texture):
        super().__init__(
            parent=scene,
            position=position,
            model='cube',
            texture=load_texture(TEXTURES[texture]),
            color=color.white,
            highlight_color=color.lime,
            collider='box'
        )

class World:
    def __init__(self):
        self.noise = PerlinNoise(octaves=4, seed=SEED)
        self.generate_terrain()
        self.setup_player()
        self.setup_ui()

    def generate_terrain(self):
        # Генерация базового ландшафта
        for x in range(-CHUNK_SIZE*WORLD_SIZE, CHUNK_SIZE*WORLD_SIZE):
            for z in range(-CHUNK_SIZE*WORLD_SIZE, CHUNK_SIZE*WORLD_SIZE):
                height = int(self.noise([x/32, z/32]) * 8 + 12)
                
                # Бедрок
                Voxel((x, -16, z), 'bedrock')
                
                # Каменные слои
                for y in range(-15, height-4):
                    Voxel((x, y, z), 'stone')
                
                # Земля
                for y in range(height-4, height):
                    Voxel((x, y, z), 'dirt')
                
                # Трава
                Voxel((x, height, z), 'grass')

    def setup_player(self):
        self.player = FirstPersonController(
            position=(0, 100, 0),
            speed=8,
            mouse_sensitivity=Vec2(80, 80),
            jump_height=2,
            gravity=1
        )
        self.player.inventory = ['grass', 'dirt', 'stone']
        self.player.selected = 0

    def setup_ui(self):
        # Hotbar
        self.hotbar = Entity(
            parent=camera.ui,
            model='quad',
            texture='white_cube',
            color=color.dark_gray,
            scale=(0.45, 0.08),
            position=(0, -0.45)
        )

        # Слоты инвентаря
        self.slots = []
        for i in range(3):
            slot = Entity(
                parent=self.hotbar,
                model='quad',
                scale=(0.15, 0.15),
                position=(-0.3 + i*0.15, 0),
                texture=load_texture(TEXTURES[self.player.inventory[i]])
            )
            self.slots.append(slot)

    def input(self, key):
        if key == 'escape':
            quit()
        
        # Выбор слота
        if key in '123':
            self.player.selected = int(key)-1
            self.update_hotbar()
        
        # Разрушение блока
        if key == 'left mouse down':
            hit = raycast(self.player.position, self.player.forward, distance=5)
            if hit.entity:
                destroy(hit.entity)
        
        # Установка блока
        if key == 'right mouse down':
            hit = raycast(self.player.position, self.player.forward, distance=5)
            if hit.entity:
                pos = hit.entity.position + hit.normal
                Voxel(pos, self.player.inventory[self.player.selected])

    def update_hotbar(self):
        for i, slot in enumerate(self.slots):
            if i == self.player.selected:
                slot.color = color.gold
            else:
                slot.color = color.white

    def update(self):
        # Обновление позиции горячей панели
        self.hotbar.position = (0, -0.45 + (abs(math.sin(time.time()*10)) * 0.01 if held_keys['w'] or held_keys['a'] or held_keys['s'] or held_keys['d'] else 0))

# Запуск игры
if __name__ == '__main__':
    world = World()
    mouse.locked = True
    app.run()
