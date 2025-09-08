import pygame
import sys
import random
import string
import pygame.camera
import time

# Initialize Pygame
pygame.init()
pygame.camera.init()

# Screen dimensions
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Webcam Lobby Chat")

# Colors
BACKGROUND = (25, 25, 40)
ACCENT = (70, 100, 200)
LIGHT_ACCENT = (100, 140, 240)
TEXT_COLOR = (230, 230, 250)
BUTTON_COLOR = (60, 180, 100)
BUTTON_HOVER = (80, 200, 120)
INPUT_BG = (40, 40, 60)
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)

# Fonts
font_large = pygame.font.SysFont("Arial", 32)
font_medium = pygame.font.SysFont("Arial", 24)
font_small = pygame.font.SysFont("Arial", 18)

# Lobby state
class LobbyState:
    MENU = 0
    LOBBY = 1
    CHAT = 2

current_state = LobbyState.MENU
lobby_code = ""
invite_input = ""
chat_input = ""
chat_messages = []
webcam_active = False
camera = None
webcam_image = None
last_frame_time = 0
fps = 30

# Generate a random lobby code
def generate_lobby_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# Draw a button with text
def draw_button(surface, x, y, width, height, color, hover_color, text, text_color=WHITE):
    mouse_x, mouse_y = pygame.mouse.get_pos()
    rect = pygame.Rect(x, y, width, height)
    
    # Check if mouse is hovering over the button
    if rect.collidepoint(mouse_x, mouse_y):
        pygame.draw.rect(surface, hover_color, rect, border_radius=8)
    else:
        pygame.draw.rect(surface, color, rect, border_radius=8)
    
    # Draw button text
    text_surf = font_medium.render(text, True, text_color)
    text_rect = text_surf.get_rect(center=rect.center)
    surface.blit(text_surf, text_rect)
    
    return rect

# Draw a text input field
def draw_input(surface, x, y, width, height, text, active=False):
    rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(surface, INPUT_BG, rect, border_radius=5)
    pygame.draw.rect(surface, ACCENT if active else LIGHT_ACCENT, rect, 2, border_radius=5)
    
    text_surf = font_medium.render(text, True, TEXT_COLOR)
    surface.blit(text_surf, (x + 10, y + (height - text_surf.get_height()) // 2))
    
    # Draw cursor if active
    if active:
        cursor_x = x + 10 + font_medium.size(text)[0]
        pygame.draw.line(surface, TEXT_COLOR, (cursor_x, y + 10), (cursor_x, y + height - 10), 2)
    
    return rect

# Draw the menu screen
def draw_menu():
    screen.fill(BACKGROUND)
    
    # Title
    title = font_large.render("Webcam Lobby Chat", True, LIGHT_ACCENT)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))
    
    # Create lobby button
    create_btn = draw_button(screen, WIDTH // 2 - 150, 200, 300, 60, BUTTON_COLOR, BUTTON_HOVER, "Create Lobby")
    
    # Join lobby section
    join_title = font_medium.render("Join with Code:", True, TEXT_COLOR)
    screen.blit(join_title, (WIDTH // 2 - join_title.get_width() // 2, 300))
    
    # Input field for invite code
    input_rect = draw_input(screen, WIDTH // 2 - 150, 340, 300, 50, invite_input, current_state == LobbyState.MENU)
    
    # Join button
    join_btn = draw_button(screen, WIDTH // 2 - 80, 410, 160, 50, ACCENT, LIGHT_ACCENT, "Join")
    
    return create_btn, input_rect, join_btn

# Draw the lobby screen
def draw_lobby():
    screen.fill(BACKGROUND)
    
    # Lobby code display
    code_text = font_large.render(f"Lobby Code: {lobby_code}", True, LIGHT_ACCENT)
    screen.blit(code_text, (WIDTH // 2 - code_text.get_width() // 2, 50))
    
    # Instructions
    instructions = font_medium.render("Share this code with others to invite them to the lobby", True, TEXT_COLOR)
    screen.blit(instructions, (WIDTH // 2 - instructions.get_width() // 2, 100))
    
    # Webcam preview area (simulated until activated)
    webcam_rect = pygame.Rect(WIDTH // 2 - 200, 160, 400, 300)
    pygame.draw.rect(screen, INPUT_BG, webcam_rect, border_radius=8)
    
    if webcam_active and webcam_image:
        # Scale the webcam image to fit the preview area
        scaled_img = pygame.transform.scale(webcam_image, (400, 300))
        screen.blit(scaled_img, webcam_rect.topleft)
    else:
        webcam_text = font_medium.render("Webcam Inactive", True, TEXT_COLOR)
        screen.blit(webcam_text, (webcam_rect.centerx - webcam_text.get_width() // 2, 
                                 webcam_rect.centery - webcam_text.get_height() // 2))
    
    # Toggle webcam button
    webcam_btn = draw_button(screen, WIDTH // 2 - 100, 480, 200, 50, 
                            BUTTON_HOVER if webcam_active else BUTTON_COLOR, 
                            BUTTON_HOVER, 
                            "Turn Off Webcam" if webcam_active else "Turn On Webcam")
    
    # Start chat button
    chat_btn = draw_button(screen, WIDTH // 2 - 100, 550, 200, 50, ACCENT, LIGHT_ACCENT, "Enter Chat")
    
    return webcam_btn, chat_btn

# Draw the chat screen
def draw_chat():
    screen.fill(BACKGROUND)
    
    # Header with lobby code
    header = font_medium.render(f"Chat - Lobby: {lobby_code}", True, LIGHT_ACCENT)
    screen.blit(header, (20, 20))
    
    # Webcam toggle button in header
    webcam_btn = draw_button(screen, WIDTH - 220, 15, 200, 40, 
                            BUTTON_HOVER if webcam_active else BUTTON_COLOR, 
                            BUTTON_HOVER, 
                            "Webcam: ON" if webcam_active else "Webcam: OFF")
    
    # Chat messages area
    chat_bg = pygame.Rect(20, 70, WIDTH - 260, HEIGHT - 160)
    pygame.draw.rect(screen, INPUT_BG, chat_bg, border_radius=8)
    
    # Webcam preview area (if active)
    if webcam_active:
        webcam_rect = pygame.Rect(WIDTH - 220, 70, 200, 150)
        pygame.draw.rect(screen, INPUT_BG, webcam_rect, border_radius=8)
        
        if webcam_image:
            scaled_img = pygame.transform.scale(webcam_image, (200, 150))
            screen.blit(scaled_img, webcam_rect.topleft)
        else:
            webcam_text = font_small.render("Webcam Active", True, TEXT_COLOR)
            screen.blit(webcam_text, (webcam_rect.centerx - webcam_text.get_width() // 2, 
                                     webcam_rect.centery - webcam_text.get_height() // 2))
    
    # Display chat messages
    y_offset = chat_bg.bottom - 30
    for message in reversed(chat_messages[-20:]):  # Show last 20 messages
        msg_surface = font_small.render(message, True, TEXT_COLOR)
        if y_offset - msg_surface.get_height() < chat_bg.top:
            break
        screen.blit(msg_surface, (chat_bg.left + 10, y_offset - msg_surface.get_height()))
        y_offset -= msg_surface.get_height() + 5
    
    # Message input field
    input_rect = draw_input(screen, 20, HEIGHT - 70, WIDTH - 140, 50, chat_input, True)
    
    # Send button
    send_btn = draw_button(screen, WIDTH - 110, HEIGHT - 70, 90, 50, ACCENT, LIGHT_ACCENT, "Send")
    
    return webcam_btn, input_rect, send_btn

# Initialize webcam
def init_webcam():
    global camera, webcam_active
    
    try:
        cameras = pygame.camera.list_cameras()
        if cameras:
            camera = pygame.camera.Camera(cameras[0], (640, 480))
            camera.start()
            webcam_active = True
            return True
        else:
            print("No camera detected")
            return False
    except Exception as e:
        print(f"Error initializing camera: {e}")
        return False

# Main game loop
clock = pygame.time.Clock()
running = True

while running:
    current_time = time.time()
    mouse_pos = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        elif event.type == pygame.KEYDOWN:
            if current_state == LobbyState.MENU:
                if event.key == pygame.K_BACKSPACE:
                    invite_input = invite_input[:-1]
                elif event.key == pygame.K_RETURN:
                    if invite_input:
                        lobby_code = invite_input.upper()
                        current_state = LobbyState.LOBBY
                else:
                    if len(invite_input) < 10 and event.unicode.isprintable():
                        invite_input += event.unicode
                        
            elif current_state == LobbyState.CHAT:
                if event.key == pygame.K_BACKSPACE:
                    chat_input = chat_input[:-1]
                elif event.key == pygame.K_RETURN:
                    if chat_input.strip():
                        chat_messages.append(f"Guest: {chat_input}")
                        chat_input = ""
                else:
                    if len(chat_input) < 100 and event.unicode.isprintable():
                        chat_input += event.unicode
                        
        elif event.type == pygame.MOUSEBUTTONDOWN