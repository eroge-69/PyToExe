from ursina import *
from ursina.sequence import Sequence

app = Ursina()
window.title = "2D Platformer"
camera.orthographic = True
camera.fov = 20

# === Game State ===
game_over = False
game_won = False
score = 0
timer_value = 300
player = None
goal_flag = None
platforms, enemies, coins = [], [], []

# === Load Textures ===
player_texture = load_texture('player_sprite_sheet.png')

# === UI Elements ===
game_over_text = Text(text='GAME OVER\nPress any key to restart', origin=(0, 0), scale=2, color=color.red, enabled=False)
game_win_text = Text(text='YOU WIN!\nPress any key to play again', origin=(0, 0), scale=2, color=color.green, enabled=False)
timer_text = Text(text=f"Time: {timer_value}", position=(-0.85, 0.45), scale=1.5, color=color.white)
score_text = Text(text=f"Coins: {score}", position=(-0.85, 0.4), scale=1.5, color=color.white)

# === Background ===
bg = Entity(model='quad', texture='bg.jpg', scale=(80, 40), z=10)

# === Ground ===
def create_ground():
    for x in range(-10, 50):
        Entity(model='cube', texture='brick.png', scale=(1, 1), position=(x, -4), collider='box')

# === Platforms ===
def create_platforms():
    coords = [(4, -1), (8, 1), (12, 3), (16, 2), (20, 4), (24, 1), (30, 2), (34, 3), (38, 2), (42, 4)]
    for x, y in coords:
        p = Entity(model='quad', texture='brick.png', scale=(2, 0.5), position=(x, y), collider='box', color=color.gray)
        platforms.append(p)

# === Ceilings ===
def create_ceilings():
    coords = [(6, 6), (14, 7), (22, 8)]
    for x, y in coords:
        Entity(model='quad', texture='brick.png', scale=(2, 0.5), position=(x, y), collider='box', color=color.dark_gray)

# === Enemies ===
def create_enemies():
    coords = [
        (10, -3), (18, -3), (26, -3), (32, -3), (36, -3), (40, -3), (45, -3),
        (12, 4), (16, 5), (22, 6), (30, 3)
    ]
    for x, y in coords:
        e = Entity(model='quad', texture='enemy.png', scale=(1, 1), position=(x, y), collider='box')
        e.direction = 1
        e.speed = 2
        e.start_x = x - 2
        e.end_x = x + 2
        enemies.append(e)

# === Coins ===
def create_coins():
    coords = [(x, y + 1) for x, y in [
        (4, -1), (8, 1), (12, 3), (16, 2), (20, 4), (24, 1), (6, 6),
        (14, 7), (22, 8), (28, 2), (2, 0), (32, 2), (36, 3), (40, 4), (44, 3)
    ]]
    for x, y in coords:
        c = Entity(model='quad', texture='coin.png', scale=0.5, position=(x, y), collider='box')
        coins.append(c)

# === Goal Flag ===
def create_goal():
    global goal_flag
    goal_flag = Entity(model='quad', texture='flag.png', scale=(1, 1.5), position=(48, -3), collider='box')

# === Destroy All Entities ===
def destroy_all():
    for e in scene.entities.copy():
        if e not in [bg, game_over_text, game_win_text, timer_text, score_text]:
            destroy(e)
    platforms.clear()
    enemies.clear()
    coins.clear()

# === Game Over ===
def player_die():
    global game_over
    player.enabled = False
    game_over = True
    game_over_text.enabled = True

# === Game Win ===
def player_win():
    global game_won
    player.enabled = False
    game_won = True
    game_win_text.enabled = True

# === Timer Countdown ===
def timer_tick():
    global timer_value
    if not game_over and not game_won:
        timer_value -= 1
        timer_text.text = f"Time: {timer_value}"
        if timer_value <= 0:
            player_die()

# Timer sequence
timer_sequence = Sequence(Func(timer_tick), Wait(1), loop=True)
timer_sequence.start()

# === Sprite Animation Setup ===
frame_count = 4
frame_index = 0
frame_speed = 4  # frames/sec

# === Game Start ===
def start_game():
    global player, game_over, game_won, score, timer_value, frame_index
    destroy_all()

    camera.position = (0, 0)
    timer_value = 300
    frame_index = 0
    score = 0
    game_over = False
    game_won = False
    game_over_text.enabled = False
    game_win_text.enabled = False
    timer_text.text = f"Time: {timer_value}"
    score_text.text = f"Coins: {score}"

    player = Entity(
        model='quad',  # Use 'quad' for 2D sprite animation
        texture=player_texture,
        position=(0, -3.25),
        scale=(1.5, 2),
        collider='box',
        texture_scale=(1 / 4, 1),  # Assuming 4 frames in sprite sheet (horizontal)
        texture_offset=(0, 0),
    )

    player.velocity_y = 0
    player.gravity = -20

    create_ground()
    create_platforms()
    create_ceilings()
    create_enemies()
    create_coins()
    create_goal()

# === Main Game Update ===
def update():
    global frame_index, score

    if not game_over and not game_won:
        # === Animate player ===
        if held_keys['a'] or held_keys['d']:
            frame_index += time.dt * frame_speed
            frame_index %= frame_count
            player.texture_scale = (1 / frame_count, 1)
            player.texture_offset = (frame_index // 1 / frame_count, 0)
        else:
            player.texture_offset = (0, 0)

        # === Movement ===
        if held_keys['a']:
            player.x -= 4 * time.dt
            player.rotation_y = 180
        if held_keys['d']:
            player.x += 4 * time.dt
            player.rotation_y = 0

        # === Gravity and Jumping ===
        player.y += player.velocity_y * time.dt
        player.velocity_y += player.gravity * time.dt

        hit_info = player.intersects()
        if hit_info.hit and hit_info.normal.y > 0:
            player.velocity_y = 0

            # Snap player Y position exactly on top of the collided entity
            player_bottom = player.y - player.scale_y / 2
            ground_top = hit_info.entity.world_y + hit_info.entity.scale_y / 2
            offset = ground_top - player_bottom
            player.y += offset

            if held_keys['space']:
                player.velocity_y = 10

        # === Camera follow ===
        camera.x = lerp(camera.x, player.x, 0.05)
        bg.x = camera.x

        # === Falling off map ===
        if player.y < -6:
            player_die()

        # === Enemy collision ===
        for enemy in enemies:
            if player.intersects(enemy).hit:
                player_die()
            enemy.x += enemy.direction * enemy.speed * time.dt
            if enemy.x > enemy.end_x or enemy.x < enemy.start_x:
                enemy.direction *= -1

        # === Coin collection ===
        for coin in coins.copy():
            coin.rotation_y += 100 * time.dt
            if player.intersects(coin).hit:
                coins.remove(coin)
                destroy(coin)
                score += 1
                score_text.text = f"Coins: {score}"

        # === Goal reached ===
        if goal_flag and player.intersects(goal_flag).hit:
            player_win()

# === Input to Restart Game ===
def input(key):
    if game_over or game_won:
        start_game()

# === Start First Game ===
start_game()
app.run()
