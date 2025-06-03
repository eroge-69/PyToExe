from ursina import *
import random

# Initialize the Ursina application
app = Ursina()

# --- Game Variables ---
# Player speed (constant, not affected by difficulty)
PLAYER_SPEED = 1

# Bullet speed (constant)
BULLET_SPEED = 10

# Enemy speed (will be set by difficulty, then scaled by game_level_multiplier)
ENEMY_SPEED = 0.25  # Default, will be overridden by difficulty selection

# Time between enemy spawns (in seconds)
ENEMY_SPAWN_INTERVAL = 2.5

# Score
score = 0

# Game state management: 'menu', 'playing', 'game_over', 'game_won'
game_state = 'menu'

# Game level multiplier (increases enemy speed as score progresses)
game_level_multiplier = 1
# Tracks the score at which the last level-up occurred, to prevent multiple level-ups for one score milestone
last_level_score_milestone = 0

# --- UI Elements ---
# Game instructions text - placed in the top-left corner
instructions_text = Text(text='SPACE BAR - shoot; A/D - move; Q - menu; R - restart', origin=(-0.5, 0.5),
                         position=(-0.85, 0.45), scale=1.5, color=color.white)
instructions_text.disable()  # Hidden initially, enabled when playing

# Score text - placed below instructions, aligned to the left
score_text = Text(text=f'Score: {score}', origin=(-0.5, 0.5), position=(-0.85, 0.40), scale=2, color=color.white)
score_text.disable()  # Hidden initially, enabled when playing

# Level text - placed below score, aligned to the left
level_text = Text(text=f'Level: {game_level_multiplier}', origin=(-0.5, 0.5), position=(-0.85, 0.35), scale=2,
                  color=color.white)
level_text.disable()  # Hidden initially, enabled when playing

# Game over message
game_over_text = Text(text='GAME OVER!\nPress R to Restart', origin=(0, 0), scale=3, color=color.red)
game_over_text.disable()  # Hidden initially

# Game won message
game_won_text = Text(text='YOU BEAT THIS GAME!\nPress R to Restart', origin=(0, 0), scale=3, color=color.green)
game_won_text.disable()  # Hidden initially

# Menu elements
menu_title = Text(text='Emptiness By V1zoR', origin=(0, -0.5), position=(0, -0.48), scale=4, color=color.white)
difficulty_options_text = Text(
    text='1 - Easy (0.25) \n2 - Medium (0.50) \n3 - Hard (0.75)',
    origin=(0, 0.05),
    scale=1.5,
    color=color.white
)

menu_elements = [menu_title, difficulty_options_text]


# --- Player Class ---
class Player(Entity):
    def __init__(self):
        super().__init__(
            parent=camera.ui,
            model='circle',  # Changed player shape to circle
            color=color.green,
            scale=(0.1, 0.1),
            position=(0, -0.4, 0)
        )

    def update(self):
        if game_state == 'playing':
            if held_keys['a']:
                self.x -= time.dt * PLAYER_SPEED
            if held_keys['d']:
                self.x += time.dt * PLAYER_SPEED
            self.x = max(-0.8, min(0.8, self.x))

    def input(self, key):
        if key == 'space' and game_state == 'playing':
            Bullet(self.x, self.y + self.scale_y / 2)


# --- Bullet Class ---
class Bullet(Entity):
    def __init__(self, x, y):
        super().__init__(
            parent=camera.ui,
            model='quad',  # Bullets remain quad (rectangular)
            color=color.yellow,
            scale=(0.02, 0.05),
            position=(x, y, 0),
            collider='box'
        )

    def update(self):
        global score, game_level_multiplier, last_level_score_milestone, game_state, game_won_text
        if game_state == 'playing':
            self.y += time.dt * BULLET_SPEED
            if self.y > 0.6:
                destroy(self)

            for enemy in enemies:
                if self.intersects(enemy).hit:
                    score += 10
                    score_text.text = f'Score: {score}'
                    destroy(self)  # Destroy bullet
                    destroy(enemy)  # Destroy enemy
                    enemies.remove(enemy)  # Remove from active enemies list

                    # Check for level progression
                    if score >= (last_level_score_milestone + 150):
                        last_level_score_milestone = score  # Update the milestone
                        if game_level_multiplier < 3:  # Max level multiplier is 3
                            game_level_multiplier += 1
                            level_text.text = f'Level: {game_level_multiplier}'  # Update level display
                            print(f"Level Up! Current game level multiplier: {game_level_multiplier}")
                        else:  # Player is at level 3 and reached another 150 points
                            game_state = 'game_won'
                            game_won_text.enable()  # Show "You beat this game!" message
                            # Disable other game elements
                            score_text.disable()
                            level_text.disable()  # Hide level text on game won
                            instructions_text.disable()  # Hide instructions on game won
                            player.disable()
                            for e_to_destroy in enemies:  # Destroy remaining enemies
                                destroy(e_to_destroy)
                            enemies.clear()
                            for b_to_destroy in scene.entities:  # Destroy remaining bullets
                                if isinstance(b_to_destroy, Bullet):
                                    destroy(b_to_destroy)
                            # No new enemies will spawn because game_state is no longer 'playing'
                    break  # Only hit one enemy per bullet


# --- Enemy Class ---
class Enemy(Entity):
    def __init__(self, x, y):
        super().__init__(
            parent=camera.ui,
            model='circle',  # Changed enemy shape to circle
            color=color.red,
            scale=(0.08, 0.08),
            position=(x, y, 0),
            collider='box'
        )

    def update(self):
        global game_state
        global score
        global ENEMY_SPEED
        global game_level_multiplier
        if game_state == 'playing':
            # Enemy speed is now based on initial difficulty AND current game level multiplier
            self.y -= time.dt * ENEMY_SPEED * game_level_multiplier

            if self.y < -0.6:
                score -= 5
                score_text.text = f'Score: {score}'
                destroy(self)
                enemies.remove(self)
                # Optional: Game over if score drops too low
                # if score < -20: # Example threshold
                #     game_state = 'game_over'
                #     game_over_text.enable()
                #     for e in enemies:
                #         destroy(e)
                #     enemies.clear()
                #     for b in scene.entities:
                #         if isinstance(b, Bullet):
                #             destroy(b)


# --- Game Management Functions ---
enemies = []


def spawn_enemy():
    if game_state == 'playing':
        x_pos = random.uniform(-0.8, 0.8)
        enemy = Enemy(x_pos, 0.5)
        enemies.append(enemy)
    # Schedule the next enemy spawn, it will only happen if game_state is 'playing'
    invoke(spawn_enemy, delay=ENEMY_SPAWN_INTERVAL)


def start_game(difficulty_level):
    global game_state, ENEMY_SPEED, score, game_level_multiplier, last_level_score_milestone
    game_state = 'playing'
    score = 0
    score_text.text = f'Score: {score}'
    score_text.enable()  # Show score

    game_level_multiplier = 1  # Reset level multiplier
    level_text.text = f'Level: {game_level_multiplier}'  # Update level display
    level_text.enable()  # Show level text

    instructions_text.enable()  # Show instructions

    player.enable()  # Make player visible

    # Reset level progression variables
    last_level_score_milestone = 0

    # Hide menu elements
    for element in menu_elements:
        element.disable()
    game_over_text.disable()  # Ensure game over text is hidden
    game_won_text.disable()  # Ensure game won text is hidden

    # Set base enemy speed based on difficulty
    if difficulty_level == 1:
        ENEMY_SPEED = 0.25  # Easy
    elif difficulty_level == 2:
        ENEMY_SPEED = 0.50  # Medium
    elif difficulty_level == 3:
        ENEMY_SPEED = 0.75  # Hard
    print(f"Starting game with Base Enemy Speed: {ENEMY_SPEED}")

    # Ensure all previous enemies and bullets are cleared before starting
    for e in enemies:
        destroy(e)
    enemies.clear()
    for b in scene.entities:
        if isinstance(b, Bullet):
            destroy(b)

    # Start spawning enemies
    spawn_enemy()


def reset_game():
    global game_state, score, game_level_multiplier, last_level_score_milestone
    score = 0
    score_text.text = f'Score: {score}'
    score_text.disable()  # Hide score when back to menu
    level_text.disable()  # Hide level text when back to menu
    instructions_text.disable()  # Hide instructions when back to menu
    game_state = 'menu'  # Return to menu state
    game_over_text.disable()
    game_won_text.disable()  # Hide game won text
    player.disable()  # Hide player when back to menu

    # Reset level progression variables
    game_level_multiplier = 1
    last_level_score_milestone = 0

    # Destroy all existing enemies and bullets
    for e in enemies:
        destroy(e)
    enemies.clear()

    for b in scene.entities:
        if isinstance(b, Bullet):
            destroy(b)

    # Show menu elements again
    for element in menu_elements:
        element.enable()


# --- Global Input Handler ---
def input(key):
    global game_state
    if game_state == 'menu':
        if key == '1':
            start_game(1)
        elif key == '2':
            start_game(2)
        elif key == '3':
            start_game(3)
    elif game_state == 'game_over' or game_state == 'game_won':  # Allow restart from game over or game won
        if key == 'r':
            reset_game()
    # Allow 'Q' to return to menu from playing, game over, or game won state
    if key == 'q' and (game_state == 'playing' or game_state == 'game_over' or game_state == 'game_won'):
        reset_game()
    # Allow ESC to quit at any state
    if key == 'escape':
        application.quit()


# --- Game Setup ---
window.color = color.black

# Create the player (initially positioned, but its update logic depends on game_state)
player = Player()
player.disable()  # Initially hide the player when in menu state

# Initially, the game is in 'menu' state, so no enemies are spawned yet.
# The `spawn_enemy` function is invoked from `start_game` now.

# Run the Ursina application
app.run()
