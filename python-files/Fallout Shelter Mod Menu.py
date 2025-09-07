import pygame
import pydirectinput
import time
import ctypes

# Initialize pygame
pygame.init()

# Set up display
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Fallout Shelter Mod Menu')

# Define colors
purple = (128, 0, 128)
gray = (128, 128, 128)
light_gray = (200, 200, 200)

# Define fonts
font = pygame.font.SysFont(None, 36)

# Define menu options
menu_options = [
    "Modify Caps",
    "Modify Stimpacks",
    "Modify RadAway",
    "Modify Rad-X",
    "Custom Pointer",
    "Exit"
]

# Cheat Engine pointers (placeholders)
cheat_engine_pointers = {
    "Modify Caps": "2B37A7AC920",
    "Modify Stimpacks": "2B37A7AC930",
    "Modify RadAway": "0x00123458",
    "Modify Rad-X": "0x00123459",
    "Custom Pointer": ""
}

# Function to draw text
def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

# Function to write to memory (simplified)
def write_to_memory(address, value):
    process = ctypes.windll.kernel32.OpenProcess(0x001F0FFF, False, ctypes.windll.user32.GetWindowThreadProcessId(ctypes.windll.user32.GetForegroundWindow(), None))
    ctypes.windll.kernel32.WriteProcessMemory(process, address, value, 4, None)
    ctypes.windll.kernel32.CloseHandle(process)

# Main menu loop
def main_menu():
    selected = 0
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(menu_options)
                if event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(menu_options)
                if event.key == pygame.K_RETURN:
                    if menu_options[selected] in cheat_engine_pointers:
                        value = input(f"Enter value for {menu_options[selected]}: ")
                        write_to_memory(int(cheat_engine_pointers[menu_options[selected]], 16), int(value))
                    elif menu_options[selected] == "Custom Pointer":
                        custom_pointer = input("Enter custom pointer address: ")
                        value = input("Enter value to write: ")
                        write_to_memory(int(custom_pointer, 16), int(value))
                    elif menu_options[selected] == "Exit":
                        running = False

        # Draw menu
        screen.fill(purple)
        for i, option in enumerate(menu_options):
            if i == selected:
                draw_text(option, font, light_gray, screen, 20, 20 + i * 40)
            else:
                draw_text(option, font, gray, screen, 20, 20 + i * 40)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main_menu()