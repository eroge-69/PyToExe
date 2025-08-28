import pygame
import random
import time
import math
import json
from pygame.locals import *
import pygame._sdl2 as sdl2  # For XInput controller support

# Initialize Pygame
pygame.init()
pygame.font.init()
pygame.joystick.init()

# Screen settings
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)  # Fullscreen mode
WIDTH, HEIGHT = pygame.display.get_surface().get_size()  # Get actual screen resolution
pygame.display.set_caption("Spark & Sip")
clock = pygame.time.Clock()

# Colors
BG_COLOR = (20, 20, 30)  # Dark background
ACCENT_COLOR = (255, 150, 180)  # Softer neon pink
SECONDARY_ACCENT = (100, 255, 100)  # Brighter neon green
TEXT_COLOR = (255, 255, 255)
BUTTON_COLOR = (50, 50, 70)
HOVER_COLOR = (80, 80, 100)
CONTROLLER_HOVER_COLOR = (0, 255, 255)  # Cyan for controller
CONTROLLER_PULSE_COLOR = (0, 200, 200)  # Slightly darker cyan
ACTIVE_FIELD_COLOR = (255, 50, 50)  # For active text field
DISABLED_COLOR = (30, 30, 30)  # For disabled buttons
SELECTED_COLOR = (255, 150, 200)  # For selected gender/theme buttons
PARTICLE_COLOR = (255, 255, 200)  # Light yellow for particles
SHADOW_COLOR = (0, 0, 0, 100)  # Semi-transparent black for shadows
THEME_COLORS = {
    "romantic": (200, 100, 150),  # Pink/purple for romantic
    "playful": (255, 200, 100),   # Bright yellow for playful
    "kinky": (100, 50, 150),      # Deep purple for kinky
    "friends_with_benefits": (0, 180, 180)  # Teal for friends with benefits
}

# Fonts
title_font = pygame.font.SysFont("arialblack", int(48 * HEIGHT / 720))
button_font = pygame.font.SysFont("helvetica, arial", int(24 * HEIGHT / 720), bold=True)
dare_font = pygame.font.SysFont("arial", int(32 * HEIGHT / 720))
status_font = pygame.font.SysFont("helvetica, arial", int(18 * HEIGHT / 720), bold=True)

# Load dares from external file
try:
    with open('dares.json', 'r') as f:
        dares = json.load(f)
except FileNotFoundError:
    print("dares.json not found. Using empty dares dictionary.")
    dares = {"romantic": {}, "playful": {}, "kinky": {}, "friends_with_benefits": {}}

# Particle class for sparkles and hearts
class Particle:
    def __init__(self, x, y, vx, vy, life, shape="circle", color=PARTICLE_COLOR):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = life
        self.shape = shape
        self.color = color

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

    def draw(self, surface):
        alpha = int(255 * (self.life / self.max_life))
        size = int(3 * HEIGHT / 720 * (self.life / self.max_life))
        if self.shape == "circle":
            pygame.draw.circle(surface, (*self.color, alpha), (int(self.x), int(self.y)), size)
        elif self.shape == "heart":
            heart_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(heart_surface, (*self.color, alpha), (size // 2, size // 2), size // 2)
            pygame.draw.circle(heart_surface, (*self.color, alpha), (size * 3 // 2, size // 2), size // 2)
            pygame.draw.polygon(heart_surface, (*self.color, alpha), [
                (size, 0), (size * 2, size), (size, size * 2), (0, size)
            ])
            surface.blit(heart_surface, (int(self.x - size), int(self.y - size)))

# Game state
class GameState:
    def __init__(self):
        self.reset()

    def reset(self):
        self.state = "menu"
        self.player1_name = ""
        self.player2_name = ""
        self.player1_gender = None
        self.player2_gender = None
        self.player1_points = 0
        self.player2_points = 0
        self.current_level = 1
        self.max_level = 6
        self.theme = "romantic"
        self.mode = None
        self.selected_levels = []
        self.current_dare = ""
        self.dare_timer = None
        self.active_field = None
        self.input_text = ""
        self.anim_alpha = 0
        self.current_player = 0
        self.first_dare = True
        self.dare_count = {1: 0, 2: 0}
        self.total_time = 600  # Default 10 minutes (in seconds)
        self.start_time = None  # Track game start time
        self.keyboard_input = ""
        self.keyboard_pos = (0, 0)
        self.using_controller = False  # Track input source
        self.controller_focus = None  # Track focused element (input field, slider, button)
        self.used_dares = set()  # Track used dares to prevent repeats

# Input field class
class InputField:
    def __init__(self, x, y, width, height, label):
        self.rect = pygame.Rect(x, y, width, height)
        self.label = label
        self.text = ""
        self.active = False
        self.controller_hovered = False
        self.hovered = False
        self.scale = 1.0
        self.target_scale = 1.0
        self.scale_speed = 0.1

    def update(self):
        if abs(self.scale - self.target_scale) > 0.01:
            self.scale += (self.target_scale - self.scale) * self.scale_speed

    def draw(self, surface, pulse_alpha):
        scaled_rect = pygame.Rect(
            self.rect.x - int(self.rect.width * (self.scale - 1) / 2),
            self.rect.y - int(self.rect.height * (self.scale - 1) / 2),
            int(self.rect.width * self.scale),
            int(self.rect.height * self.scale)
        )
        shadow_rect = pygame.Rect(scaled_rect.x + 5, scaled_rect.y + 5, scaled_rect.width, scaled_rect.height)
        pygame.draw.rect(surface, SHADOW_COLOR, shadow_rect, border_radius=5)
        color = ACTIVE_FIELD_COLOR if self.active else BUTTON_COLOR
        pygame.draw.rect(surface, color, scaled_rect, border_radius=5)
        if self.controller_hovered:
            border_color = (
                CONTROLLER_PULSE_COLOR[0],
                CONTROLLER_PULSE_COLOR[1],
                CONTROLLER_PULSE_COLOR[2],
                int(255 * (0.7 + 0.3 * math.sin(pulse_alpha)))
            )
            pygame.draw.rect(surface, border_color[:3], scaled_rect, 6, border_radius=5)
        else:
            pygame.draw.rect(surface, SECONDARY_ACCENT if self.hovered else ACCENT_COLOR, scaled_rect, 2, border_radius=5)
        text_surf = button_font.render(self.text + ("|" if self.active else ""), True, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=scaled_rect.center)
        surface.blit(text_surf, text_rect)
        label_surf = button_font.render(self.label, True, TEXT_COLOR)
        surface.blit(label_surf, (scaled_rect.x, scaled_rect.y - 30 * HEIGHT / 720))

    def check_click(self, pos):
        return self.rect.collidepoint(pos)

    def set_controller_hover(self, hovered):
        self.controller_hovered = hovered
        self.target_scale = 1.15 if hovered or self.hovered else 1.0

# Button class
class Button:
    def __init__(self, text, x, y, width, height, action, enabled=True):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.action = action
        self.enabled = enabled
        self.hovered = False
        self.selected = False
        self.controller_hovered = False
        self.scale = 1.0
        self.target_scale = 1.0
        self.scale_speed = 0.1

    def update(self):
        if abs(self.scale - self.target_scale) > 0.01:
            self.scale += (self.target_scale - self.scale) * self.scale_speed

    def draw(self, surface, pulse_alpha):
        scaled_rect = pygame.Rect(
            self.rect.x - int(self.rect.width * (self.scale - 1) / 2),
            self.rect.y - int(self.rect.height * (self.scale - 1) / 2),
            int(self.rect.width * self.scale),
            int(self.rect.height * self.scale)
        )
        shadow_rect = pygame.Rect(scaled_rect.x + 5, scaled_rect.y + 5, scaled_rect.width, scaled_rect.height)
        pygame.draw.rect(surface, SHADOW_COLOR, shadow_rect, border_radius=10)
        color = SELECTED_COLOR if self.selected else (CONTROLLER_HOVER_COLOR if self.controller_hovered and self.enabled else HOVER_COLOR if self.hovered and self.enabled else BUTTON_COLOR if self.enabled else DISABLED_COLOR)
        pygame.draw.rect(surface, color, scaled_rect, border_radius=10)
        if self.controller_hovered and self.enabled:
            border_color = (
                CONTROLLER_PULSE_COLOR[0],
                CONTROLLER_PULSE_COLOR[1],
                CONTROLLER_PULSE_COLOR[2],
                int(255 * (0.7 + 0.3 * math.sin(pulse_alpha)))
            )
            pygame.draw.rect(surface, border_color[:3], scaled_rect, 6, border_radius=10)
        else:
            pygame.draw.rect(surface, SECONDARY_ACCENT if self.hovered else ACCENT_COLOR, scaled_rect, 2 if not self.selected else 4, border_radius=10)
        text_surf = button_font.render(self.text, True, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=scaled_rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, pos):
        if self.enabled:
            self.hovered = self.rect.collidepoint(pos)
            self.target_scale = 1.15 if self.hovered or self.controller_hovered else 1.0

    def set_controller_hover(self, hovered):
        self.controller_hovered = hovered
        self.target_scale = 1.15 if hovered or self.hovered else 1.0

    def click(self):
        if self.enabled:
            self.action()

# Slider class for time and naughtiness
class Slider:
    def __init__(self, x, y, width, height, label, min_val, max_val):
        self.rect = pygame.Rect(x, y, width, height)
        self.label = label
        self.min_val = min_val
        self.max_val = max_val
        self.value = min_val
        self.knob_rect = pygame.Rect(x, y, 20 * WIDTH / 1280, height)
        self.hovered = False
        self.dragging = False
        self.controller_hovered = False

    def update(self, mouse_pos, mouse_pressed):
        if self.rect.collidepoint(mouse_pos) and mouse_pressed:
            self.dragging = True
        elif not mouse_pressed:
            self.dragging = False
        if self.dragging:
            self.knob_rect.x = max(self.rect.x, min(mouse_pos[0] - 10 * WIDTH / 1280, self.rect.x + self.rect.width - 20 * WIDTH / 1280))
            self.value = int(self.min_val + (self.max_val - self.min_val) * (self.knob_rect.x - self.rect.x) / (self.rect.width - 20 * WIDTH / 1280))

    def set_controller_value(self, direction):
        step = (self.rect.width - 20 * WIDTH / 1280) // (self.max_val - self.min_val)
        self.knob_rect.x += direction * step
        self.knob_rect.x = max(self.rect.x, min(self.knob_rect.x, self.rect.x + self.rect.width - 20 * WIDTH / 1280))
        self.value = int(self.min_val + (self.max_val - self.min_val) * (self.knob_rect.x - self.rect.x) / (self.rect.width - 20 * WIDTH / 1280))

    def draw(self, surface, pulse_alpha):
        shadow_rect = pygame.Rect(self.rect.x + 5, self.rect.y + 5, self.rect.width, self.rect.height)
        pygame.draw.rect(surface, SHADOW_COLOR, shadow_rect, border_radius=5)
        pygame.draw.rect(surface, BUTTON_COLOR, self.rect, border_radius=5)
        pygame.draw.rect(surface, ACCENT_COLOR, self.knob_rect, border_radius=5)
        if self.controller_hovered:
            border_color = (
                CONTROLLER_PULSE_COLOR[0],
                CONTROLLER_PULSE_COLOR[1],
                CONTROLLER_PULSE_COLOR[2],
                int(255 * (0.7 + 0.3 * math.sin(pulse_alpha)))
            )
            pygame.draw.rect(surface, border_color[:3], self.rect, 6, border_radius=5)
        label_text = f"{self.label}: {self.value} min" if self.label == "Total Time" else f"{self.label}: {self.value}"
        label_surf = button_font.render(label_text, True, TEXT_COLOR)
        surface.blit(label_surf, (self.rect.x, self.rect.y - 30 * HEIGHT / 720))

# Render text with animation
def render_text_plain(text, font, color, max_width, top=False, scale=1.0):
    words = text.split(' ')
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)
    rendered_lines = []
    for line in lines:
        text_surf = font.render(line, True, color)
        scaled_surf = pygame.transform.scale(text_surf, (int(text_surf.get_width() * scale), int(text_surf.get_height() * scale)))
        rendered_lines.append(scaled_surf)
    total_height = sum(line.get_height() for line in rendered_lines)
    y_start = 50 * HEIGHT / 720 if top else (HEIGHT - total_height) // 2
    return [(text_surf, (WIDTH // 2 - text_surf.get_width() // 2, y_start + i * text_surf.get_height())) for i, text_surf in enumerate(rendered_lines)]

# Animated background with theme-based colors
def draw_animated_background(surface, time, theme):
    base_color = THEME_COLORS.get(theme, BG_COLOR)
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        wave = math.sin(time + y * 0.01) * 20
        color = (
            int(BG_COLOR[0] * (1 - ratio) + base_color[0] * ratio + wave),
            int(BG_COLOR[1] * (1 - ratio) + base_color[1] * ratio + wave),
            int(BG_COLOR[2] * (1 - ratio) + base_color[2] * ratio + wave)
        )
        color = tuple(max(0, min(255, c)) for c in color)
        pygame.draw.line(surface, color, (0, y), (WIDTH, y))

# Main game function
def main():
    # Initialize joystick
    joystick = None
    joystick_count = pygame.joystick.get_count()
    print(f"Number of joysticks detected: {joystick_count}")
    if joystick_count > 0:
        try:
            joystick = pygame.joystick.Joystick(0)
            if not joystick.get_init():
                joystick.init()
            print(f"Joystick name: {joystick.get_name()}")
            print(f"Number of buttons: {joystick.get_numbuttons()}")
            print(f"Number of axes: {joystick.get_numaxes()}")
            print(f"Number of hats: {joystick.get_numhats()}")
            print("Controller detected - use D-pad to navigate, A to select, B to go back")
        except pygame.error as e:
            print(f"Error initializing joystick: {e}")
            joystick = None
    else:
        print("No controller detected. Check connection/drivers.")

    # Initialize game state and UI variables
    game_state = GameState()
    input_fields = []
    sliders = []
    particles = []
    buttons = []
    controller_elements = {
        "menu": [],
        "player_setup": [],
        "mode_select": [],
        "level_select": [],
        "game": [],
        "win": [],
        "keyboard": []
    }
    controller_nav_pos = (0, 0)  # (row, col)
    last_dpad_time = 0
    pulse_alpha = 0

    # Define helper functions
    def create_menu_buttons():
        new_buttons = []
        new_buttons.append(Button("Start Game", WIDTH//2 - 100 * WIDTH / 1280, 300 * HEIGHT / 720, 200 * WIDTH / 1280, 50 * HEIGHT / 720, lambda: set_state("player_setup")))
        new_buttons.append(Button("Exit", WIDTH//2 - 100 * WIDTH / 1280, 400 * HEIGHT / 720, 200 * WIDTH / 1280, 50 * HEIGHT / 720, lambda: pygame.quit() or exit()))
        return new_buttons

    def reset_game_state():
        game_state.player1_points = 0
        game_state.player2_points = 0
        game_state.current_level = 1
        game_state.current_player = 0
        game_state.first_dare = True
        game_state.dare_count = {1: 0, 2: 0}
        game_state.current_dare = ""
        game_state.dare_timer = None
        game_state.start_time = None
        game_state.selected_levels = []
        game_state.mode = None
        game_state.used_dares.clear()  # Clear used dares
        print("Game state reset")

    def update_controller_focus():
        nonlocal controller_nav_pos
        for f in input_fields:
            f.set_controller_hover(False)
        for s in sliders:
            s.controller_hovered = False
        for b in buttons:
            b.set_controller_hover(False)
        if game_state.state in controller_elements and controller_elements[game_state.state]:
            row, col = controller_nav_pos
            max_cols = max(c for r, c, _ in controller_elements[game_state.state] if r == row) + 1 if any(r == row for r, _, _ in controller_elements[game_state.state]) else 1
            max_rows = max(r for r, _, _ in controller_elements[game_state.state]) + 1
            col = min(col, max_cols - 1)
            row = min(row, max_rows - 1)
            controller_nav_pos = (row, col)
            for r, c, elem in controller_elements[game_state.state]:
                if r == row and c == col:
                    game_state.controller_focus = elem
                    if isinstance(elem, Button):
                        elem.set_controller_hover(True)
                        print(f"Controller focus: Button {elem.text} at nav_pos {controller_nav_pos}")
                    elif isinstance(elem, InputField):
                        elem.set_controller_hover(True)
                        print(f"Controller focus: Input field {elem.label} at nav_pos {controller_nav_pos}")
                    elif isinstance(elem, Slider):
                        elem.controller_hovered = True
                        print(f"Controller focus: Slider {elem.label} at nav_pos {controller_nav_pos}")
                    break
        else:
            game_state.controller_focus = None
            print(f"Controller focus: None (no elements in state {game_state.state})")

    def set_state(state):
        nonlocal buttons, input_fields, sliders, controller_nav_pos
        game_state.state = state
        game_state.anim_alpha = 0
        game_state.controller_focus = None
        controller_nav_pos = (0, 0)
        new_buttons = []
        new_sliders = []
        if state == "menu":
            reset_game_state()
            new_buttons = create_menu_buttons()
            controller_elements[state] = [(i, 0, new_buttons[i]) for i in range(len(new_buttons))]
        elif state == "player_setup":
            reset_game_state()
            game_state.player1_name = ""
            game_state.player2_name = ""
            game_state.player1_gender = None
            game_state.player2_gender = None
            if not input_fields:
                input_fields[:] = [
                    InputField(WIDTH//4 - 100 * WIDTH / 1280, 250 * HEIGHT / 720, 200 * WIDTH / 1280, 40 * HEIGHT / 720, "Player 1 Name"),
                    InputField(WIDTH*3//4 - 100 * WIDTH / 1280, 250 * HEIGHT / 720, 200 * WIDTH / 1280, 40 * HEIGHT / 720, "Player 2 Name")
                ]
            new_buttons.append(Button("Male", WIDTH//4 - 100 * WIDTH / 1280, 350 * HEIGHT / 720, 100 * WIDTH / 1280, 50 * HEIGHT / 720, lambda: set_gender(1, "male")))
            new_buttons.append(Button("Female", WIDTH//4 + 50 * WIDTH / 1280, 350 * HEIGHT / 720, 100 * WIDTH / 1280, 50 * HEIGHT / 720, lambda: set_gender(1, "female")))
            new_buttons.append(Button("Male", WIDTH*3//4 - 100 * WIDTH / 1280, 350 * HEIGHT / 720, 100 * WIDTH / 1280, 50 * HEIGHT / 720, lambda: set_gender(2, "male")))
            new_buttons.append(Button("Female", WIDTH*3//4 + 50 * WIDTH / 1280, 350 * HEIGHT / 720, 100 * WIDTH / 1280, 50 * HEIGHT / 720, lambda: set_gender(2, "female")))
            new_sliders.append(Slider(WIDTH//2 - 150 * WIDTH / 1280, 450 * HEIGHT / 720, 300 * WIDTH / 1280, 20 * HEIGHT / 720, "Naughtiness", 1, 6))
            new_buttons.append(Button("Next", WIDTH//2 - 100 * WIDTH / 1280, 500 * HEIGHT / 720, 200 * WIDTH / 1280, 50 * HEIGHT / 720, lambda: set_state("mode_select"), enabled=False))
            controller_elements[state] = [
                (0, 0, input_fields[0]),
                (0, 1, input_fields[1]),
                (1, 0, new_buttons[0]),
                (1, 1, new_buttons[1]),
                (1, 2, new_buttons[2]),
                (1, 3, new_buttons[3]),
                (2, 0, new_sliders[0]),
                (3, 0, new_buttons[4])
            ]
        elif state == "mode_select":
            button_width = 150 * WIDTH / 1280
            button_width_long = 250 * WIDTH / 1280  # Longer button for Friends w/ Benefits
            button_spacing = 20 * WIDTH / 1280
            total_width = 3 * button_width + button_width_long + 3 * button_spacing
            start_x = WIDTH // 2 - total_width // 2
            new_buttons.append(Button("Single Level", WIDTH//2 - 100 * WIDTH / 1280, 200 * HEIGHT / 720, 200 * WIDTH / 1280, 50 * HEIGHT / 720, lambda: set_state("level_select") or setattr(game_state, "mode", "single")))
            new_buttons.append(Button("Progressive", WIDTH//2 - 100 * WIDTH / 1280, 300 * HEIGHT / 720, 200 * WIDTH / 1280, 50 * HEIGHT / 720, lambda: [setattr(game_state, "mode", "progressive"), setattr(game_state, "selected_levels", list(range(1, game_state.max_level + 1))), set_state("game")]))
            new_buttons.append(Button("Random Levels", WIDTH//2 - 100 * WIDTH / 1280, 400 * HEIGHT / 720, 200 * WIDTH / 1280, 50 * HEIGHT / 720, lambda: [setattr(game_state, "mode", "random"), setattr(game_state, "selected_levels", list(range(1, game_state.max_level + 1))), set_state("game")]))
            new_buttons.append(Button("Romantic", start_x, 100 * HEIGHT / 720, button_width, 50 * HEIGHT / 720, lambda: set_theme("romantic")))
            new_buttons.append(Button("Playful", start_x + button_width + button_spacing, 100 * HEIGHT / 720, button_width, 50 * HEIGHT / 720, lambda: set_theme("playful")))
            new_buttons.append(Button("Kinky", start_x + 2 * button_width + 2 * button_spacing, 100 * HEIGHT / 720, button_width, 50 * HEIGHT / 720, lambda: set_theme("kinky")))
            new_buttons.append(Button("Friends w/ Benefits", start_x + 3 * button_width + 3 * button_spacing, 100 * HEIGHT / 720, button_width_long, 50 * HEIGHT / 720, lambda: set_theme("friends_with_benefits")))
            new_sliders.append(Slider(WIDTH//2 - 150 * WIDTH / 1280, 500 * HEIGHT / 720, 300 * WIDTH / 1280, 20 * HEIGHT / 720, "Total Time", 5, 30))
            controller_elements[state] = [
                (0, 0, new_buttons[3]),
                (0, 1, new_buttons[4]),
                (0, 2, new_buttons[5]),
                (0, 3, new_buttons[6]),
                (1, 0, new_buttons[0]),
                (2, 0, new_buttons[1]),
                (3, 0, new_buttons[2]),
                (4, 0, new_sliders[0])
            ]
            for button in new_buttons:
                if button.text.lower() == game_state.theme:
                    button.selected = True
        elif state == "level_select":
            for i in range(1, game_state.max_level + 1):
                new_buttons.append(Button(f"Level {i}", WIDTH//2 - 100 * WIDTH / 1280, (100 + i*60) * HEIGHT / 720, 200 * WIDTH / 1280, 50 * HEIGHT / 720, lambda level=i: setattr(game_state, "selected_levels", [level]) or set_state("game")))
            controller_elements[state] = [(i, 0, new_buttons[i]) for i in range(len(new_buttons))]
        elif state == "game":
            game_state.player1_points = 0
            game_state.player2_points = 0
            game_state.current_player = 0
            game_state.first_dare = True
            game_state.dare_count = {1: 0, 2: 0}
            game_state.current_level = 1
            game_state.start_time = time.time()
            game_state.used_dares.clear()  # Reset used dares
            generate_dare(game_state)
            new_buttons.append(Button("Next Dare", WIDTH//2 - 100 * WIDTH / 1280, 500 * HEIGHT / 720, 200 * WIDTH / 1280, 50 * HEIGHT / 720, lambda: complete_dare(game_state)))
            new_buttons.append(Button("Skip Dare", WIDTH//2 - 100 * WIDTH / 1280, 560 * HEIGHT / 720, 200 * WIDTH / 1280, 50 * HEIGHT / 720, lambda: skip_dare(game_state)))
            new_buttons.append(Button("Back to Menu", WIDTH//2 - 100 * WIDTH / 1280, 620 * HEIGHT / 720, 200 * WIDTH / 1280, 50 * HEIGHT / 720, lambda: set_state("menu")))
            controller_elements[state] = [(i, 0, new_buttons[i]) for i in range(len(new_buttons))]
        elif state == "win":
            new_buttons.append(Button("Play Again", WIDTH//2 - 100 * WIDTH / 1280, 500 * HEIGHT / 720, 200 * WIDTH / 1280, 50 * HEIGHT / 720, lambda: set_state("player_setup")))
            new_buttons.append(Button("Exit", WIDTH//2 - 100 * WIDTH / 1280, 560 * HEIGHT / 720, 200 * WIDTH / 1280, 50 * HEIGHT / 720, lambda: pygame.quit() or exit()))
            controller_elements[state] = [(i, 0, new_buttons[i]) for i in range(len(new_buttons))]
            for _ in range(50):
                x = WIDTH // 2
                y = HEIGHT // 2
                vx = random.uniform(-5, 5)
                vy = random.uniform(-5, 5)
                particles.append(Particle(x, y, vx, vy, 60, shape="heart", color=THEME_COLORS[game_state.theme]))
        elif state == "keyboard":
            game_state.keyboard_input = ""
            keys = "ABCDEFGHIJKLMNOPQRSTUVWXYZ 0123456789"
            new_buttons.append(Button("Backspace", WIDTH//2 - 250 * WIDTH / 1280, 500 * HEIGHT / 720, 150 * WIDTH / 1280, 50 * HEIGHT / 720, lambda: setattr(game_state, "keyboard_input", game_state.keyboard_input[:-1])))
            new_buttons.append(Button("Enter", WIDTH//2 + 100 * WIDTH / 1280, 500 * HEIGHT / 720, 150 * WIDTH / 1280, 50 * HEIGHT / 720, lambda: save_keyboard_input(game_state)))
            for i, char in enumerate(keys):
                x = WIDTH//2 - 400 * WIDTH / 1280 + (i % 8) * 60 * WIDTH / 1280
                y = HEIGHT//2 - 200 * HEIGHT / 720 + (i // 8) * 60 * HEIGHT / 720
                new_buttons.append(Button(char, x, y, 50 * WIDTH / 1280, 50 * HEIGHT / 720, lambda c=char: setattr(game_state, "keyboard_input", game_state.keyboard_input + c)))
            controller_elements[state] = []
            for row in range(5):
                for col in range(8 if row < 4 else 2):
                    if row == 4:
                        idx = 0 if col == 0 else 1
                    else:
                        idx = 2 + row * 8 + col
                    controller_elements[state].append((row, col, new_buttons[idx]))
        buttons[:] = new_buttons
        sliders[:] = new_sliders
        update_controller_focus()
        print(f"State changed to: {state}, Buttons: {[b.text for b in buttons]}, Controller elements: {[(row, col, elem.text if isinstance(elem, Button) else elem.label) for row, col, elem in controller_elements[state]]}")

    def set_gender(player, gender):
        if player == 1:
            game_state.player1_gender = gender
            for button in buttons:
                if button.rect.x < WIDTH//2 and button.text in ["Male", "Female"]:
                    button.selected = (button.text.lower() == gender)
        else:
            game_state.player2_gender = gender
            for button in buttons:
                if button.rect.x > WIDTH//2 and button.text in ["Male", "Female"]:
                    button.selected = (button.text.lower() == gender)

    def set_theme(theme):
        game_state.theme = theme
        for button in buttons:
            if button.text.lower() in ["romantic", "playful", "kinky", "friends_with_benefits"]:
                button.selected = (button.text.lower() == theme)
        print(f"Theme set to: {theme}")

    def save_keyboard_input(game_state):
        if game_state.active_field and input_fields:
            if game_state.active_field == input_fields[0]:
                game_state.player1_name = game_state.keyboard_input
                game_state.active_field.text = game_state.keyboard_input
                game_state.active_field.active = False
                if len(input_fields) > 1:
                    game_state.active_field = input_fields[1]
                    game_state.active_field.active = True
                    game_state.keyboard_input = ""
                    set_state("keyboard")
                else:
                    game_state.active_field = None
                    game_state.keyboard_input = ""
                    set_state("player_setup")
            elif len(input_fields) > 1 and game_state.active_field == input_fields[1]:
                game_state.player2_name = game_state.keyboard_input
                game_state.active_field.text = game_state.keyboard_input
                game_state.active_field.active = False
                game_state.active_field = None
                game_state.keyboard_input = ""
                set_state("player_setup")
        else:
            print("No active field or input fields empty in save_keyboard_input")
            game_state.active_field = None
            game_state.keyboard_input = ""
            set_state("player_setup")

    def complete_dare(game_state):
        points = game_state.current_level * 10
        if "bonus points" in game_state.current_dare.lower():
            points += 10
        if game_state.current_player == 1:
            game_state.player1_points += points
            print(f"Completed dare for Player 1 ({game_state.player1_name}): +{points} points, Total: {game_state.player1_points}")
        else:
            game_state.player2_points += points
            print(f"Completed dare for Player 2 ({game_state.player2_name}): +{points} points, Total: {game_state.player2_points}")
        for _ in range(10):
            x = WIDTH // 2
            y = HEIGHT // 2
            vx = random.uniform(-3, 3)
            vy = random.uniform(-3, 3)
            particles.append(Particle(x, y, vx, vy, 30, shape="heart", color=THEME_COLORS[game_state.theme]))
        if game_state.mode == "progressive":
            categories = ["neutral"] if game_state.player1_gender == game_state.player2_gender else [
                f"{game_state.player1_gender}_to_{game_state.player2_gender}",
                f"{game_state.player2_gender}_to_{game_state.player1_gender}"
            ]
            level_str = str(game_state.current_level)
            all_used = True
            for category in categories:
                available_dares = dares[game_state.theme][level_str].get(category, [])
                unused_dares = [dare for dare in available_dares if dare not in game_state.used_dares]
                if unused_dares:
                    all_used = False
                    break
            if all_used or (game_state.dare_count[1] >= 6 and game_state.dare_count[2] >= 6):
                game_state.used_dares.clear()
                game_state.current_level += 1
                game_state.dare_count = {1: 0, 2: 0}
                if game_state.current_level > game_state.max_level:
                    set_state("win")
                    print(f"Progressive mode completed: All dares exhausted or 6 dares per player at level {game_state.current_level - 1}")
                else:
                    print(f"Level increased to {game_state.current_level} (all dares used or 6 dares completed)")
            generate_dare(game_state)
        else:
            if time.time() - game_state.start_time >= game_state.total_time:
                set_state("win")
                print(f"Time's up: {game_state.total_time} seconds elapsed")
            else:
                generate_dare(game_state)

    def skip_dare(game_state):
        if game_state.current_player == 1:
            game_state.player1_points -= 5
            print(f"Skipped dare for Player 1 ({game_state.player1_name}): -5 points, Total: {game_state.player1_points}")
        else:
            game_state.player2_points -= 5
            print(f"Skipped dare for Player 2 ({game_state.player2_name}): -5 points, Total: {game_state.player2_points}")
        generate_dare(game_state)

    def generate_dare(game_state):
        if game_state.first_dare:
            game_state.current_player = 1
            game_state.first_dare = False
            game_state.dare_count[game_state.current_player] = 0
        else:
            game_state.current_player = 2 if game_state.current_player == 1 else 1
        
        if game_state.mode == "progressive" and game_state.dare_count[game_state.current_player] >= 6:
            categories = ["neutral"] if game_state.player1_gender == game_state.player2_gender else [
                f"{game_state.player1_gender}_to_{game_state.player2_gender}",
                f"{game_state.player2_gender}_to_{game_state.player1_gender}"
            ]
            level_str = str(game_state.current_level)
            all_used = True
            for category in categories:
                available_dares = dares[game_state.theme][level_str].get(category, [])
                unused_dares = [dare for dare in available_dares if dare not in game_state.used_dares]
                if unused_dares:
                    all_used = False
                    break
            if all_used or (game_state.dare_count[1] >= 6 and game_state.dare_count[2] >= 6):
                game_state.used_dares.clear()
                game_state.current_level += 1
                game_state.dare_count = {1: 0, 2: 0}
                if game_state.current_level > game_state.max_level:
                    set_state("win")
                    print(f"Progressive mode completed: All dares exhausted or 6 dares per player at level {game_state.current_level - 1}")
                    return
                else:
                    print(f"Level increased to {game_state.current_level} (all dares used or 6 dares completed)")
        
        game_state.dare_count[game_state.current_player] += 1
        
        if game_state.mode == "random":
            game_state.current_level = random.choice(game_state.selected_levels)
        elif game_state.mode == "single":
            game_state.current_level = game_state.selected_levels[0]
        
        if game_state.current_player == 1:
            performer_gender = game_state.player1_gender
            target_gender = game_state.player2_gender
            performer_name = game_state.player1_name
            target_name = game_state.player2_name
        else:
            performer_gender = game_state.player2_gender
            target_gender = game_state.player1_gender
            performer_name = game_state.player2_name
            target_name = game_state.player1_name
        dare_type = f"{performer_gender}_to_{target_gender}"
        if performer_gender == target_gender or dare_type not in dares[game_state.theme].get(str(game_state.current_level), {}):
            dare_type = "neutral"
        try:
            available_dares = dares[game_state.theme][str(game_state.current_level)][dare_type]
            unused_dares = [dare for dare in available_dares if dare not in game_state.used_dares]
            if not unused_dares:
                if game_state.mode == "progressive":
                    game_state.used_dares.clear()
                    game_state.current_level += 1
                    game_state.dare_count = {1: 0, 2: 0}
                    if game_state.current_level > game_state.max_level:
                        set_state("win")
                        print(f"Progressive mode completed: All dares exhausted at level {game_state.current_level - 1}")
                        return
                    available_dares = dares[game_state.theme][str(game_state.current_level)][dare_type]
                    unused_dares = [dare for dare in available_dares if dare not in game_state.used_dares]
                    if not unused_dares:
                        set_state("win")
                        print(f"No dares available for theme {game_state.theme}, level {game_state.current_level}, type {dare_type}")
                        return
                else:
                    set_state("win")
                    print(f"No dares available for theme {game_state.theme}, level {game_state.current_level}, type {dare_type}")
                    return
            dare = random.choice(unused_dares)
            game_state.used_dares.add(dare)
        except (KeyError, IndexError):
            print(f"Error: No dares found for theme {game_state.theme}, level {game_state.current_level}, type {dare_type}")
            dare = "No dare available, please select another theme or level."
            set_state("win")
        game_state.current_dare = dare.format(male=game_state.player1_name, female=game_state.player2_name, performer=performer_name, target=target_name)
        game_state.dare_timer = time.time()
        print(f"Generated dare for Player {game_state.current_player} ({performer_name}): {game_state.current_dare}")

    # Explicitly set the initial state to "menu"
    set_state("menu")

    running = True
    while running:
        current_time = time.time()
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        pulse_alpha += 0.1

        if random.random() < 0.05:
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            vx = random.uniform(-2, 2)
            vy = random.uniform(-2, 2)
            particles.append(Particle(x, y, vx, vy, 60, shape="heart" if game_state.theme in ["romantic", "kinky", "friends_with_benefits"] else "circle", color=THEME_COLORS[game_state.theme]))

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == MOUSEBUTTONDOWN:
                for field in input_fields[:]:
                    if field.check_click(mouse_pos):
                        game_state.active_field = field
                        field.active = True
                        game_state.keyboard_input = ""
                        game_state.using_controller = False
                        try:
                            controller_nav_pos = next((r, c) for r, c, e in controller_elements[game_state.state] if e == field)
                            update_controller_focus()
                            print(f"Mouse clicked: Input field {field.label}")
                        except StopIteration:
                            print(f"Mouse clicked: Input field {field.label} not in controller elements")
                for button in buttons[:]:
                    if button.rect.collidepoint(mouse_pos):
                        try:
                            controller_nav_pos = next((r, c) for r, c, e in controller_elements[game_state.state] if e == button)
                            button.click()
                            update_controller_focus()
                            print(f"Mouse clicked: Button {button.text}")
                        except StopIteration:
                            print("Mouse click: Button not in controller elements, skipping")
                for slider in sliders:
                    slider.update(mouse_pos, True)
            elif event.type == MOUSEBUTTONUP:
                for slider in sliders:
                    slider.dragging = False
            elif event.type == KEYDOWN and game_state.active_field and not game_state.using_controller:
                if event.key == K_RETURN:
                    if game_state.active_field == input_fields[0]:
                        game_state.player1_name = input_fields[0].text
                        if len(input_fields) > 1:
                            game_state.active_field = input_fields[1]
                            input_fields[1].active = True
                            input_fields[0].active = False
                            controller_nav_pos = (0, 1)
                            update_controller_focus()
                        else:
                            game_state.active_field = None
                            controller_nav_pos = (3, 0)
                            update_controller_focus()
                    elif game_state.active_field == input_fields[1]:
                        game_state.player2_name = input_fields[1].text
                        game_state.active_field = None
                        controller_nav_pos = (3, 0)
                        update_controller_focus()
                elif event.key == K_BACKSPACE:
                    game_state.active_field.text = game_state.active_field.text[:-1]
                else:
                    game_state.active_field.text += event.unicode
            elif event.type == JOYBUTTONDOWN:
                if joystick:
                    print(f"Controller button pressed: {event.button}")
                    if event.button == 0:
                        game_state.using_controller = True
                        if game_state.state == "player_setup" and isinstance(game_state.controller_focus, InputField):
                            game_state.active_field = game_state.controller_focus
                            game_state.active_field.active = True
                            game_state.keyboard_input = ""
                            set_state("keyboard")
                            print(f"Controller selected: Input field {game_state.active_field.label}")
                        elif isinstance(game_state.controller_focus, Button):
                            game_state.controller_focus.click()
                            print(f"Controller clicked: Button {game_state.controller_focus.text}")
                        elif isinstance(game_state.controller_focus, Slider):
                            print(f"Controller focus: Slider {game_state.controller_focus.label} (use left/right to adjust)")
                    elif event.button == 1:
                        if game_state.state == "keyboard":
                            game_state.active_field.text = game_state.keyboard_input
                            game_state.active_field.active = False
                            game_state.active_field = None
                            game_state.keyboard_input = ""
                            set_state("player_setup")
                            print("Controller B: Returned to player_setup")
                        elif game_state.state == "player_setup" and game_state.active_field:
                            game_state.active_field.active = False
                            game_state.active_field = None
                            controller_nav_pos = (3, 0)
                            update_controller_focus()
                            print("Controller B: Deselected input field")
                        elif game_state.state in ["mode_select", "level_select", "game"]:
                            set_state("menu")
                            print("Controller B: Back to menu")
            elif event.type == JOYHATMOTION:
                if joystick and current_time - last_dpad_time > 0.1:
                    hat_value = joystick.get_hat(0)
                    print(f"D-pad pressed: {hat_value}")
                    if game_state.state == "keyboard":
                        max_rows = 5
                        max_cols = [8, 8, 8, 8, 2]
                        row, col = controller_nav_pos
                        if hat_value[1] == 1:
                            row = (row - 1) % max_rows
                        elif hat_value[1] == -1:
                            row = (row + 1) % max_rows
                        elif hat_value[0] == 1:
                            col = (col + 1) % max_cols[row]
                        elif hat_value[0] == -1:
                            col = (col - 1) % max_cols[row]
                        controller_nav_pos = (row, col)
                    else:
                        max_row = max(r for r, _, _ in controller_elements[game_state.state]) if controller_elements[game_state.state] else 0
                        max_cols = [max(c for r, c, _ in controller_elements[game_state.state] if r == i) + 1 for i in range(max_row + 1)] if controller_elements[game_state.state] else [1]
                        row, col = controller_nav_pos
                        if game_state.state == "menu":
                            if hat_value[1] == 1:
                                row = (row - 1) % (max_row + 1)
                            elif hat_value[1] == -1:
                                row = (row + 1) % (max_row + 1)
                        else:
                            if hat_value[1] == 1:
                                row = (row - 1) % (max_row + 1)
                            elif hat_value[1] == -1:
                                row = (row + 1) % (max_row + 1)
                            elif hat_value[0] == 1 and isinstance(game_state.controller_focus, Slider):
                                game_state.controller_focus.set_controller_value(1)
                                print(f"Controller adjusted slider: {game_state.controller_focus.label} to {game_state.controller_focus.value}")
                            elif hat_value[0] == -1 and isinstance(game_state.controller_focus, Slider):
                                game_state.controller_focus.set_controller_value(-1)
                                print(f"Controller adjusted slider: {game_state.controller_focus.label} to {game_state.controller_focus.value}")
                            elif hat_value[0] != 0:
                                col = (col + (1 if hat_value[0] == 1 else -1)) % max_cols[row]
                        controller_nav_pos = (row, col)
                    update_controller_focus()
                    last_dpad_time = current_time

        pygame.event.pump()

        for button in buttons:
            button.update()
            button.check_hover(mouse_pos)
        for field in input_fields:
            field.update()
            field.hovered = field.check_click(mouse_pos)
        for slider in sliders:
            slider.update(mouse_pos, mouse_pressed)

        for button in buttons:
            if button.text == "Next":
                button.enabled = bool(game_state.player1_name and game_state.player2_name and game_state.player1_gender and game_state.player2_gender)
        if input_fields:
            game_state.player1_name = input_fields[0].text
        if len(input_fields) > 1:
            game_state.player2_name = input_fields[1].text
        if sliders and game_state.state == "player_setup":
            game_state.max_level = sliders[0].value
        if sliders and game_state.state == "mode_select":
            game_state.total_time = sliders[0].value * 60

        if game_state.state == "game" and game_state.dare_timer and current_time - game_state.dare_timer > 20:
            if game_state.current_player == 1:
                game_state.player1_points -= 5
                print(f"Time's up for Player 1 ({game_state.player1_name}): -5 points, Total: {game_state.player1_points}")
            else:
                game_state.player2_points -= 5
                print(f"Time's up for Player 2 ({game_state.player2_name}): -5 points, Total: {game_state.player2_points}")
            generate_dare(game_state)

        draw_animated_background(screen, current_time, game_state.theme)
        game_state.anim_alpha = min(game_state.anim_alpha + 10, 255)
        dare_text_scale = 0.8 + 0.2 * (game_state.anim_alpha / 255) if game_state.state == "game" else 1.0

        particles[:] = [p for p in particles if p.life > 0]
        for particle in particles:
            particle.update()
            particle.draw(screen)

        if game_state.state == "menu":
            title_lines = render_text_plain("Spark & Sip", title_font, TEXT_COLOR, WIDTH - 100 * WIDTH / 1280, top=True)
            for text_surf, (x, y) in title_lines:
                text_surf.set_alpha(game_state.anim_alpha)
                screen.blit(text_surf, (x, y))
            for button in buttons:
                button.draw(screen, pulse_alpha)

        elif game_state.state == "player_setup":
            for field in input_fields:
                field.draw(screen, pulse_alpha)
            for slider in sliders:
                slider.draw(screen, pulse_alpha)
            for button in buttons:
                button.draw(screen, pulse_alpha)

        elif game_state.state == "mode_select":
            for button in buttons:
                button.draw(screen, pulse_alpha)
            for slider in sliders:
                slider.draw(screen, pulse_alpha)

        elif game_state.state == "level_select":
            for button in buttons:
                button.draw(screen, pulse_alpha)

        elif game_state.state == "game":
            p1_text = button_font.render(f"{game_state.player1_name}: {game_state.player1_points} pts", True, TEXT_COLOR)
            p2_text = button_font.render(f"{game_state.player2_name}: {game_state.player2_points} pts", True, TEXT_COLOR)
            screen.blit(p1_text, (50 * WIDTH / 1280, 50 * HEIGHT / 720))
            screen.blit(p2_text, (WIDTH - p2_text.get_width() - 50 * WIDTH / 1280, 50 * HEIGHT / 720))
            level_text = button_font.render(f"Level: {game_state.current_level}", True, SECONDARY_ACCENT)
            screen.blit(level_text, (WIDTH//2 - level_text.get_width()//2, 100 * HEIGHT / 720))
            if game_state.mode in ["single", "random"]:
                time_left = max(0, game_state.total_time - int(current_time - game_state.start_time))
                timer_text = button_font.render(f"Time Left: {time_left//60}:{time_left%60:02d}", True, ACTIVE_FIELD_COLOR)
                screen.blit(timer_text, (WIDTH//2 - timer_text.get_width()//2, 130 * HEIGHT / 720))
            if game_state.mode == "progressive":
                dare_count_text = button_font.render(f"Dares: {game_state.dare_count[game_state.current_player]}/6 (Level {game_state.current_level})", True, TEXT_COLOR)
            else:
                dare_count_text = button_font.render(f"Dare: {game_state.dare_count[game_state.current_player]}", True, TEXT_COLOR)
            screen.blit(dare_count_text, (WIDTH//2 - dare_count_text.get_width()//2, 160 * HEIGHT / 720))
            if game_state.current_dare:
                dare_lines = render_text_plain(game_state.current_dare, dare_font, TEXT_COLOR, WIDTH - 100 * WIDTH / 1280, scale=dare_text_scale)
                for text_surf, (x, y) in dare_lines:
                    text_surf.set_alpha(game_state.anim_alpha)
                    screen.blit(text_surf, (x, y))
            for button in buttons:
                button.draw(screen, pulse_alpha)

        elif game_state.state == "win":
            win_text = render_text_plain("You've Conquered Spark & Sip!", title_font, TEXT_COLOR, WIDTH - 100 * WIDTH / 1280, top=True)
            for text_surf, (x, y) in win_text:
                text_surf.set_alpha(game_state.anim_alpha)
                screen.blit(text_surf, (x, y))
            score_text = button_font.render(f"Final Scores: {game_state.player1_name}: {game_state.player1_points}, {game_state.player2_name}: {game_state.player2_points}", True, TEXT_COLOR)
            screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2 - 50 * HEIGHT / 720))
            for button in buttons:
                button.draw(screen, pulse_alpha)

        elif game_state.state == "keyboard":
            input_text = button_font.render(game_state.keyboard_input + "|", True, TEXT_COLOR)
            screen.blit(input_text, (WIDTH//2 - input_text.get_width()//2, HEIGHT//2 - 250 * HEIGHT / 720))
            for button in buttons:
                button.draw(screen, pulse_alpha)

        controller_status = "Controller Connected: Yes" if joystick else "Controller Connected: No (Use mouse/keyboard)"
        status_surf = status_font.render(controller_status, True, TEXT_COLOR)
        screen.blit(status_surf, (10 * WIDTH / 1280, HEIGHT - 30 * HEIGHT / 720))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()