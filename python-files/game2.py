import pygame
import math
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("My Generic Ass Web Game also its me Josh HIIII")

# Colors
BLACK = (10, 10, 20)  # Darker background for contrast
WHITE = (180, 180, 200, 200)  # Softer white with slight transparency
RED = (100, 100, 255, 200)  # Softer red for points
BLUE = (100, 100, 255, 200)  # Blue for selected points

# Point class for particles
class Point:
    def __init__(self, x, y, is_boundary):
        self.original_x = x
        self.original_y = y
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.is_fixed = is_boundary
        self.is_boundary = is_boundary
        self.is_selected = False  # For right-click interaction

# Connection class for springs
class Connection:
    def __init__(self, p1, p2, rest_length):
        self.p1 = p1
        self.p2 = p2
        self.rest_length = rest_length

# Parameters
SPACING = 40
MARGIN = 50
NUM_COLS = int((WIDTH - 2 * MARGIN) / SPACING) + 1
NUM_ROWS = int((HEIGHT - 2 * MARGIN) / SPACING) + 1
SPRING_STIFFNESS = 0.15  # Smooth response
DAMPING = 0.96  # Less oscillation
ATTRACTION_STRENGTH = 120.0  # Responsive interaction
SHAKE_STRENGTH = 0.02  # Subtle shake
DISSOLVE_BURST = 8  # Controlled dissolve
RESET_STIFFNESS = 0.025  # Smooth reappearance
RESET_THRESHOLD = 3  # Snappy reset
SELECT_RADIUS = 30  # Radius for selecting points

# Create points in a grid
points = []
for i in range(NUM_ROWS):
    for j in range(NUM_COLS):
        x = MARGIN + j * SPACING
        y = MARGIN + i * SPACING
        is_boundary = (i == 0 or i == NUM_ROWS - 1 or j == 0 or j == NUM_COLS - 1)
        points.append(Point(x, y, is_boundary))

# Create connections (horizontal, vertical, diagonals)
connections = []
for i in range(NUM_ROWS):
    for j in range(NUM_COLS):
        idx = i * NUM_COLS + j
        if j < NUM_COLS - 1:
            connections.append(Connection(points[idx], points[idx + 1], SPACING))
        if i < NUM_ROWS - 1:
            connections.append(Connection(points[idx], points[idx + NUM_COLS], SPACING))
        if j < NUM_COLS - 1 and i < NUM_ROWS - 1:
            connections.append(Connection(points[idx], points[idx + NUM_COLS + 1], SPACING * math.sqrt(2)))
            connections.append(Connection(points[idx + 1], points[idx + NUM_COLS], SPACING * math.sqrt(2)))

# Game states
dissolving = False
resetting = False
last_mx, last_my = pygame.mouse.get_pos()

# Enable alpha blending
screen.set_alpha(None)

# Main loop
running = True
clock = pygame.time.Clock()

while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left-click to dissolve
                if not dissolving and not resetting:
                    dissolving = True
                    for p in points:
                        p.is_fixed = False
                        p.is_selected = False
                        p.vx += random.uniform(-DISSOLVE_BURST, DISSOLVE_BURST)
                        p.vy += random.uniform(-DISSOLVE_BURST, DISSOLVE_BURST)
            elif event.button == 3:  # Right-click to select points
                if not dissolving and not resetting:
                    mx, my = event.pos
                    for p in points:
                        if not p.is_fixed:
                            dist = math.hypot(p.x - mx, p.y - my)
                            p.is_selected = dist < SELECT_RADIUS
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not dissolving and not resetting:
                # Space key for random jiggle
                for p in points:
                    if not p.is_fixed:
                        p.vx += random.uniform(-2, 2)
                        p.vy += random.uniform(-2, 2)
            elif event.key == pygame.K_r and not dissolving and not resetting:
                # 'R' key to toggle fixed state
                for p in points:
                    if p.is_selected and not p.is_boundary:
                        p.is_fixed = not p.is_fixed

    # Get mouse position
    mx, my = pygame.mouse.get_pos()

    # Calculate mouse movement for shake
    mouse_dx = mx - last_mx
    mouse_dy = my - last_my
    mouse_speed = math.hypot(mouse_dx, mouse_dy)
    last_mx, last_my = mx, my

    # Apply forces based on state
    if dissolving:
        for p in points:
            p.vx *= 0.99
            p.vy *= 0.99
            p.x += p.vx
            p.y += p.vy

        # Transition to resetting after a short time (0.5 seconds)
        if pygame.time.get_ticks() % 1000 > 500:  # 500ms delay
            dissolving = False
            resetting = True
            for p in points:
                p.x = p.original_x + random.uniform(-200, 200)
                p.y = p.original_y + random.uniform(-200, 200)
                p.vx = 0
                p.vy = 0
                p.is_selected = False

    elif resetting:
        for p in points:
            dx = p.original_x - p.x
            dy = p.original_y - p.y
            dist = math.hypot(dx, dy)
            if dist > 0:
                force = RESET_STIFFNESS * dist
                p.vx += force * dx / dist
                p.vy += force * dy / dist

        for conn in connections:
            dx = conn.p2.x - conn.p1.x
            dy = conn.p2.y - conn.p1.y
            dist = math.hypot(dx, dy)
            if dist == 0:
                continue
            force = SPRING_STIFFNESS * (dist - conn.rest_length)
            fx = force * dx / dist
            fy = force * dy / dist

            conn.p1.vx += fx
            conn.p1.vy += fy
            conn.p2.vx -= fx
            conn.p2.vy -= fy

        for p in points:
            p.vx *= DAMPING
            p.vy *= DAMPING
            p.x += p.vx
            p.y += p.vy

        if all(math.hypot(p.x - p.original_x, p.y - p.original_y) < RESET_THRESHOLD for p in points):
            resetting = False
            for p in points:
                p.x = p.original_x
                p.y = p.original_y
                p.vx = 0
                p.vy = 0
                p.is_fixed = p.is_boundary
                p.is_selected = False

    else:
        for p in points:
            if not p.is_fixed:
                # Attraction to mouse
                dx = mx - p.x
                dy = my - p.y
                dist = math.hypot(dx, dy) + 1e-5
                force = ATTRACTION_STRENGTH / (dist ** 1.5)
                p.vx += force * dx / dist
                p.vy += force * dy / dist

                # Subtle shake on cursor move
                if mouse_speed > 0:
                    shake = SHAKE_STRENGTH * mouse_speed
                    p.vx += random.uniform(-shake, shake)
                    p.vy += random.uniform(-shake, shake)

        for conn in connections:
            dx = conn.p2.x - conn.p1.x
            dy = conn.p2.y - conn.p1.y
            dist = math.hypot(dx, dy)
            if dist == 0:
                continue
            force = SPRING_STIFFNESS * (dist - conn.rest_length)
            fx = force * dx / dist
            fy = force * dy / dist

            if not conn.p1.is_fixed:
                conn.p1.vx += fx
                conn.p1.vy += fy
            if not conn.p2.is_fixed:
                conn.p2.vx -= fx
                conn.p2.vy -= fy

        for p in points:
            if not p.is_fixed:
                p.vx *= DAMPING
                p.vy *= DAMPING
                p.x += p.vx
                p.y += p.vy

    # Draw connections with anti-aliased lines
    for conn in connections:
        pygame.draw.aaline(screen, WHITE, (int(conn.p1.x), int(conn.p1.y)), (int(conn.p2.x), int(conn.p2.y)))

    # Draw points (blue if selected, red otherwise)
    for p in points:
        color = BLUE if p.is_selected else RED
        pygame.draw.circle(screen, color, (int(p.x), int(p.y)), 2)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
