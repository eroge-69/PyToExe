import pygame
import sys
import os
import json

# ������������� Pygame
pygame.init()

# ��������� ������
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SimulatorTurbo: ��������� �������")
clock = pygame.time.Clock()

# �����
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 100, 255)   # ����
RED = (255, 50, 0)     # �����
GREEN = (0, 200, 0)    # �����
YELLOW = (255, 255, 0) # ������

# ����� ��� ����������
save_folder = os.path.join(os.path.expanduser("~"), "Desktop", "SimulatorTurbo")
if not os.path.exists(save_folder):
    os.makedirs(save_folder)
save_file = os.path.join(save_folder, "save.json")

# �������� ���������
def load_game():
    if os.path.exists(save_file):
        try:
            with open(save_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"water": 0, "fire": 0, "earth": 0, "air": 0}
    return {"water": 0, "fire": 0, "earth": 0, "air": 0}

# ���������� ���������
def save_game(state):
    with open(save_file, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=4)

# �������� ������
def animate_element(element, color):
    center_x, center_y = WIDTH // 2, HEIGHT // 2
    for i in range(20):
        screen.fill(BLACK)
        radius = 100 + i * 2
        pygame.draw.circle(screen, color, (center_x, center_y), radius, 5)
        font = pygame.font.Font(None, 48)
        text = font.render(element, True, color)
        screen.blit(text, (center_x - 20, center_y - 20))
        pygame.display.flip()
        clock.tick(15)
    pygame.draw.circle(screen, WHITE, (center_x, center_y), 100, 2)

# ��������� ������
def draw_button(screen, text, x, y, color, text_color=WHITE):
    font = pygame.font.Font(None, 36)
    button_rect = pygame.Rect(x, y, 150, 50)
    pygame.draw.rect(screen, color, button_rect)
    text_surf = font.render(text, True, text_color)
    text_rect = text_surf.get_rect(center=button_rect