import pygame
import sys
import os

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 900, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dual Font On-Screen Keyboard")

# Colors
BACKGROUND = (45, 45, 60)
KEY_COLOR = (100, 100, 140)
KEY_PRESSED = (70, 170, 100)
TEXT_COLOR = (240, 240, 240)
BORDER_COLOR = (60, 60, 80)
SWITCH_BUTTON = (80, 130, 200)
SWITCH_HOVER = (100, 150, 220)

# Fonts
english_font = pygame.font.SysFont("Arial", 20)
alternative_font = pygame.font.SysFont("Times New Roman", 22)
title_font = pygame.font.SysFont("Arial", 28, bold=True)

# Keyboard layout (top row to bottom row)
keyboard_layout = [
    ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "=", "Backspace"],
    ["Tab", "q", "w", "e", "r", "t", "y", "u", "i", "o", "p", "[", "]", "\\"],
    ["Caps", "a", "s", "d", "f", "g", "h", "j", "k", "l", ";", "'", "Enter"],
    ["Shift", "z", "x", "c", "v", "b", "n", "m", ",", ".", "/", "Shift"],
    ["Ctrl", "Win", "Alt", "Space", "Alt", "Menu", "Ctrl"]
]

# Alternative font mapping (example: Greek letters)
alternative_chars = {
    "1": "¹", "2": "²", "3": "³", "4": "⁴", "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹", "0": "⁰", "-": "⁻", "=": "⁼",
    "q": "α", "w": "β", "e": "ε", "r": "ρ", "t": "τ", "y": "υ", "u": "μ", "i": "ι", "o": "ο", "p": "π", "[": "{", "]": "}", "\\": "|",
    "a": "α", "s": "σ", "d": "δ", "f": "φ", "g": "γ", "h": "η", "j": "ξ", "k": "κ", "l": "λ", ";": ":", "'": "\"",
    "z": "ζ", "x": "χ", "c": "ψ", "v": "ω", "b": "б", "n": "ν", "m": "м", ",": "<", ".": ">", "/": "?",
    "Space": "_______"
}

# Key sizes and positions
key_width = 60
key_height = 50
key_spacing = 8
start_x = 50
start_y = 100

# Current font state
use_alternative_font = False

# Draw a key on the keyboard
def draw_key(x, y, width, height, main_text, alt_text, is_pressed=False):
    color = KEY_PRESSED if is_pressed else KEY_COLOR
    pygame.draw.rect(screen, color, (x, y, width, height), 0, 6)
    pygame.draw.rect(screen, BORDER_COLOR, (x, y, width, height), 2, 6)
    
    # Draw English text (top left)
    eng_text = english_font.render(main_text, True, TEXT_COLOR)
    screen.blit(eng_text, (x + 5, y + 5))
    
    # Draw alternative text (bottom right)
    alt_text_surface = alternative_font.render(alt_text, True, TEXT_COLOR)
    screen.blit(alt_text_surface, (x + width - alt_text_surface.get_width() - 5, 
                                  y + height - alt_text_surface.get_height() - 5))

# Draw the entire keyboard
def draw_keyboard(pressed_keys):
    y = start_y
    for row in keyboard_layout:
        x = start_x
        for key in row:
            width = key_width
            # Adjust width for special keys
            if key == "Backspace":
                width = key_width * 1.5
            elif key == "Tab":
                width = key_width * 1.5
            elif key == "Caps":
                width = key_width * 1.75
            elif key == "Enter":
                width = key_width * 1.75
            elif key == "Shift":
                width = key_width * 2.25
            elif key == "Space":
                width = key_width * 5
            elif key in ["Ctrl", "Win", "Alt", "Menu"]:
                width = key_width * 1.25
            
            # Get alternative character
            alt_char = alternative_chars.get(key, key)
            
            # Draw the key
            draw_key(x, y, width, key_height, key, alt_char, key.lower() in pressed_keys)
            
            x += width + key_spacing
        y += key_height + key_spacing

# Draw the font switch button
def draw_switch_button():
    button_width, button_height = 250, 40
    button_x = WIDTH // 2 - button_width // 2
    button_y = 40
    
    # Check if mouse is hovering over the button
    mouse_x, mouse_y = pygame.mouse.get_pos()
    hover = (button_x <= mouse_x <= button_x + button_width and 
             button_y <= mouse_y <= button_y + button_height)
    
    color = SWITCH_HOVER if hover else SWITCH_BUTTON
    pygame.draw.rect(screen, color, (button_x, button_y, button_width, button_height), 0, 8)
    
    button_text = "Switch to Greek Reference" if not use_alternative_font else "Switch to English Keyboard"
    text_surface = english_font.render(button_text, True, TEXT_COLOR)
    screen.blit(text_surface, (button_x + button_width // 2 - text_surface.get_width() // 2, 
                              button_y + button_height // 2 - text_surface.get_height() // 2))
    
    return button_x, button_y, button_width, button_height

# Draw instructions
def draw_instructions():
    instructions = [
        "Instructions:",
        "1. Use the button above to switch between English and Greek keyboard views",
        "2. The top-left of each key shows the English character",
        "3. The bottom-right shows the corresponding Greek character",
        "4. Press keys on your physical keyboard to see visual feedback"
    ]
    
    y = HEIGHT - 130
    for instruction in instructions:
        text = english_font.render(instruction, True, TEXT_COLOR)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, y))
        y += 25

# Main function
def main():
    global use_alternative_font
    
    pressed_keys = set()
    clock = pygame.time.Clock()
    
    running = True
    while running:
        screen.fill(BACKGROUND)
        
        # Draw title
        title = title_font.render("Dual Font On-Screen Keyboard", True, TEXT_COLOR)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 10))
        
        # Draw switch button and get its rect
        button_rect = draw_switch_button()
        
        # Draw keyboard
        draw_keyboard(pressed_keys)
        
        # Draw instructions
        draw_instructions()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check if switch button was clicked
                x, y, width, height = button_rect
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if x <= mouse_x <= x + width and y <= mouse_y <= y + height:
                    use_alternative_font = not use_alternative_font
            elif event.type == pygame.KEYDOWN:
                pressed_keys.add(pygame.key.name(event.key).lower())
            elif event.type == pygame.KEYUP:
                key_name = pygame.key.name(event.key).lower()
                if key_name in pressed_keys:
                    pressed_keys.remove(key_name)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()