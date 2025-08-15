from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from random import randint

app = Ursina()

# === Game State ===
night = 1
hunger = 100
time_passed = 0
night_duration = 60  # seconds per night

# === Environment ===
ground = Entity(model='plane', texture='grass', scale=(100, 1, 100), collider='box')

# === Trees ===
tree_model = load_model('cube')
tree_texture = load_texture('white_cube')

for _ in range(60):
    x = randint(-40, 40)
    z = randint(-40, 40)
    Entity(
        model=tree_model,
        texture=tree_texture,
        color=color.green,
        scale=(1, 3, 1),
        position=(x, 1.5, z),
        collider='box'
    )

# === Player ===
player = FirstPersonController()
player.gravity = 0.5
player.cursor.visible = True

# === Lighting & Sky ===
DirectionalLight(y=2, z=3, shadows=True)
sky = Sky()

# === UI ===
night_text = Text(text=f'🌙 Night: {night}', position=(-0.85, 0.45), scale=1.5, origin=(0,0), background=True)
hunger_text = Text(text=f'🍗 Hunger: {hunger}', position=(-0.85, 0.4), scale=1.5, origin=(0,0), background=True)

# === Game Logic ===
def update():
    global hunger, night, time_passed

    # Decrease hunger slowly
    hunger -= time.dt * 0.5
    if hunger < 0:
        hunger = 0

    # Update UI
    hunger_text.text = f'🍗 Hunger: {int(hunger)}'

    # Time logic
    time_passed += time.dt
    if time_passed >= night_duration:
        night += 1
        time_passed = 0
        night_text.text = f'🌙 Night: {night}'

        # Change sky color slightly every night
        r = max(0, 0.5 - night * 0.01)
        g = max(0, 0.6 - night * 0.005)
        b = min(1, 0.7 + night * 0.01)
        sky.color = color.rgb(r*255, g*255, b*255)


app.run()
