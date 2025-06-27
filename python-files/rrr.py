from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()

# --- Текстуры блоков ---
grass_texture = load_texture('assets/grass.png')
stone_texture = load_texture('assets/stone.png')
brick_texture = load_texture('assets/brick.png')
dirt_texture = load_texture('assets/dirt.png')
wood_texture = load_texture('assets/wood.png')  # Новая текстура дерева
leaves_texture = load_texture('assets/leaves.png') # Новая текстура листвы
sand_texture = load_texture('assets/sand.png') # Новая текстура песка

block_textures = {
    0: grass_texture,  # 0 - Трава
    1: stone_texture,  # 1 - Камень
    2: brick_texture,  # 2 - Кирпич
    3: dirt_texture,   # 3 - Земля
    4: wood_texture,    # 4 - Дерево
    5: leaves_texture,  # 5 - Листва
    6: sand_texture      # 6 - Песок
}

# --- Настройка неба ---
class Sky(Entity):  # Custom Sky class for gradient
    def __init__(self):
        super().__init__(
            parent=scene,
            model='sphere',
            texture='sky_default',  # Убедитесь, что у вас есть текстура sky_default.png в папке assets
            scale=500,
            double_sided=True,
            rotation_y=0
        )
        self.shader = 'unlit'

    def update(self):
        self.rotation_y += time.dt * 1  # Медленно вращаем небо

sky = Sky()

# --- Настройка платформы из блоков ---
platform_size = 16  # Размер платформы (количество блоков в ширину и длину)
platform_height = 1  # Высота платформы в блоках
platform_block_type = 0  # Тип блока для платформы (0 - трава)

for x in range(platform_size):
    for z in range(platform_size):
        for y in range(platform_height):
            Entity(
                model='cube',
                texture=block_textures[platform_block_type],
                position=(x - platform_size // 2, -y, z - platform_size // 2),  # Центрируем платформу
                collider='box',
                scale=1
            )

# --- Персонаж ---
player = FirstPersonController(position=(0, 1, 0), speed=10) # Немного поднимаем персонажа над платформой

# --- Инвентарь (простой) ---
block_types = [0, 1, 2, 3, 4, 5, 6]  # Типы блоков для размещения (добавлено дерево и листва)
current_block_type = 0
# block_display = Text(text=f'Block: {current_block_type}', origin=(0, 0.4), scale=2, color=color.black)  # Position changed to be visible
# block_display = Text(text=f'Block: {current_block_type}', origin=(0, -0.5), scale=2, color=color.black)  # Text to show block type
# block_display.enabled = False  # Hide text
#  --- Убрал отрисовку текста---

def next_block():
    global current_block_type
    current_block_type = (current_block_type + 1) % len(block_types)
    # block_display.text = f'Block: {current_block_type}'  # Update text # No Text
    print(f"Selected block type: {current_block_type}")

def input(key):
    global current_block_type

    if key == 'e':
        next_block()

    if key == 'scroll up':
        next_block()

    if key == 'scroll down':
        current_block_type = (current_block_type - 1) % len(block_types)
        # block_display.text = f'Block: {current_block_type}'  # Update text # No Text
        print(f"Selected block type: {current_block_type}")

    if key == 'left mouse down':
        hit_info = raycast(camera.world_position, camera.forward, distance=5)
        if hit_info.hit and hit_info.entity != sky:
            destroy(hit_info.entity)

    if key == 'right mouse down':
        hit_info = raycast(camera.world_position, camera.forward, distance=5, ignore=[player, sky])

        if hit_info.hit and hit_info.entity != sky: # added check to prevent placing blocks in sky
            place_position = hit_info.entity.position + hit_info.normal
            Entity(model='cube', texture=block_textures[block_types[current_block_type]], position=place_position, collider='box', scale=1)


# --- Запуск игры ---
app.run()
