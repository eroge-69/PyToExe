
import pygame
import sys

pygame.init()
pygame.joystick.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 1920, 1080
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Jumanji 2D Split-Screen with PS5 Controllers")

WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

PLAYER_SPEED = 5

viewports = [
    pygame.Rect(0, 0, SCREEN_WIDTH // 3, SCREEN_HEIGHT),
    pygame.Rect(SCREEN_WIDTH // 3, 0, SCREEN_WIDTH // 3, SCREEN_HEIGHT),
    pygame.Rect(2 * SCREEN_WIDTH // 3, 0, SCREEN_WIDTH // 3, SCREEN_HEIGHT),
]

players = [
    {
        "pos": pygame.Vector2(100, 100),
        "color": RED,
        "joystick_id": 0,
        "move": pygame.Vector2(0, 0)
    },
    {
        "pos": pygame.Vector2(100, 300),
        "color": GREEN,
        "joystick_id": 1,
        "move": pygame.Vector2(0, 0)
    },
    {
        "pos": pygame.Vector2(100, 500),
        "color": BLUE,
        "joystick_id": 2,
        "move": pygame.Vector2(0, 0)
    },
]

joysticks = []
for i in range(pygame.joystick.get_count()):
    joystick = pygame.joystick.Joystick(i)
    joystick.init()
    joysticks.append(joystick)
    print(f"Joystick {i} connected: {joystick.get_name()}")

clock = pygame.time.Clock()

def get_joystick_axis(joy, axis):
    val = joy.get_axis(axis)
    if abs(val) < 0.2:
        return 0
    return val

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill((30, 30, 30))

    for i, player in enumerate(players):
        move = pygame.Vector2(0, 0)
        joy_id = player["joystick_id"]
        if joy_id < len(joysticks):
            joy = joysticks[joy_id]
            x_axis = get_joystick_axis(joy, 0)
            y_axis = get_joystick_axis(joy, 1)
            move.x = x_axis * PLAYER_SPEED
            move.y = y_axis * PLAYER_SPEED

        player["pos"] += move

        viewport = viewports[i]
        sub_surface = screen.subsurface(viewport)
        sub_surface.fill((50, 50, 50))
        pygame.draw.circle(sub_surface, player["color"], (int(player["pos"].x), int(player["pos"].y)), 20)
        pygame.draw.rect(screen, WHITE, viewport, 3)

    pygame.display.flip()
    clock.tick(60)
