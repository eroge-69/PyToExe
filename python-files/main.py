import pygame
import sys

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 700
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Trójkąt Sierpińskiego - Optymalizacja")

clock = pygame.time.Clock()

# Kolory
BG_COLOR = (30, 30, 30)
TRIANGLE_COLOR = (200, 200, 255)

# Parametry kamery i zoomu
CAMERA_WIDTH, CAMERA_HEIGHT = 1000, 1000
MARGIN = 5  # margines do optymalizacji widoczności

camera_x, camera_y = 0, 0
zoom = 1.0

# Poziom rekursji
level = 7

# Startowe punkty trójkąta (w przestrzeni świata)
A = (0, 0)
B = (1000, 0)
C = (500, 866)  # wysokość trójkąta równobocznego o boku 1000

def world_to_screen(pos):
    """Konwersja współrzędnych świata na ekran z uwzględnieniem kamery i zoomu"""
    x, y = pos
    sx = (x - camera_x) * zoom + SCREEN_WIDTH // 2
    sy = (y - camera_y) * zoom + SCREEN_HEIGHT // 2
    return (sx, sy)

def is_triangle_outside(points, rect):
    # Sprawdza, czy WSZYSTKIE punkty trójkąta są poza rect (czyli trójkąt całkowicie poza widokiem)
    for p in points:
        if rect.collidepoint(p):
            return False
    return True

def draw_triangle(surface, points, level):
    # Zamiana punktów świata na ekranowe (dla sprawdzania widoczności i rysowania)
    screen_points = [world_to_screen(p) for p in points]

    cam_rect = pygame.Rect(
        SCREEN_WIDTH // 2 - CAMERA_WIDTH // 2 * zoom - MARGIN,
        SCREEN_HEIGHT // 2 - CAMERA_HEIGHT // 2 * zoom - MARGIN,
        CAMERA_WIDTH * zoom + 2 * MARGIN,
        CAMERA_HEIGHT * zoom + 2 * MARGIN
    )

    if is_triangle_outside(screen_points, cam_rect):
        return  # Optymalizacja: nie rysuj ani nie schodź dalej

    if level == 0:
        pygame.draw.polygon(surface, TRIANGLE_COLOR, screen_points)
        return

    A, B, C = points
    AB = ((A[0] + B[0]) / 2, (A[1] + B[1]) / 2)
    BC = ((B[0] + C[0]) / 2, (B[1] + C[1]) / 2)
    CA = ((C[0] + A[0]) / 2, (C[1] + A[1]) / 2)

    draw_triangle(surface, [A, AB, CA], level - 1)
    draw_triangle(surface, [B, BC, AB], level - 1)
    draw_triangle(surface, [C, CA, BC], level - 1)

def handle_input():
    global camera_x, camera_y, zoom, level

    keys = pygame.key.get_pressed()
    speed = 10 / zoom  # ruch kamery wolniejszy przy zoomie

    if keys[pygame.K_w]:
        camera_y -= speed
    if keys[pygame.K_s]:
        camera_y += speed
    if keys[pygame.K_a]:
        camera_x -= speed
    if keys[pygame.K_d]:
        camera_x += speed

    if keys[pygame.K_z]:
        zoom *= 1.05
        if zoom > 5:  # max zoom
            zoom = 5
    if keys[pygame.K_x]:
        zoom /= 1.05
        if zoom < 0.1:  # min zoom
            zoom = 0.1

    # Zmiana poziomu rekursji (opcjonalnie)
    if keys[pygame.K_l]:
        level += 1
        if level > 10:
            level = 10
        pygame.time.wait(150)  # debounce
    if keys[pygame.K_k]:
        level -= 1
        if level < 0:
            level = 0
        pygame.time.wait(150)

def main():
    global level
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        handle_input()

        screen.fill(BG_COLOR)

        draw_triangle(screen, [A, B, C], level)

        # Info o poziomie i zoomie
        font = pygame.font.SysFont("Arial", 18)
        info = font.render(f"Level: {level} | Zoom: {zoom:.2f} | Camera: ({int(camera_x)}, {int(camera_y)})", True, (255, 255, 255))
        screen.blit(info, (10, 10))

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
