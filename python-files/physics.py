import pygame
import pymunk
import pymunk.pygame_util
import sys
import random

# Initialize
pygame.init()
WIDTH, HEIGHT = 1920, 1080  # 🖥️ Full HD resolution
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Physics Engine")
clock = pygame.time.Clock()

# Physics setup
space = pymunk.Space()
space.gravity = (0, 900)
draw_options = pymunk.pygame_util.DrawOptions(screen)

# Colors
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
RED = (255, 100, 100)
BLUE = (100, 100, 255)
ORANGE = (255, 165, 0)

# Object lists
objects = []
drag_target = None
mouse_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
drag_joint = None

# Ground
def create_ground():
    body = pymunk.Body(body_type=pymunk.Body.STATIC)
    shape = pymunk.Segment(body, (0, HEIGHT), (WIDTH, HEIGHT), 5)
    shape.friction = 1.0
    space.add(body, shape)

create_ground()

# Create red block with lighter mass
def create_block(x, y, w=60, h=60, mass=2):
    moment = pymunk.moment_for_box(mass, (w, h))
    body = pymunk.Body(mass, moment)
    body.position = x, y
    shape = pymunk.Poly.create_box(body, (w, h))
    shape.friction = 0.8
    shape.elasticity = 0.3
    shape.color = RED
    space.add(body, shape)
    objects.append((body, shape))
    return body

# Create ball
def create_ball(x, y, radius=30, mass=2):
    moment = pymunk.moment_for_circle(mass, 0, radius)
    body = pymunk.Body(mass, moment)
    body.position = x, y
    shape = pymunk.Circle(body, radius)
    shape.friction = 0.9
    shape.elasticity = 0.7
    shape.color = ORANGE
    space.add(body, shape)
    objects.append((body, shape))
    return body

# Draw buttons
font = pygame.font.SysFont(None, 24)
def draw_button(x, y, label):
    rect = pygame.Rect(x, y, 120, 30)
    pygame.draw.rect(screen, GRAY, rect)
    pygame.draw.rect(screen, BLACK, rect, 2)
    text = font.render(label, True, BLACK)
    screen.blit(text, (x + 5, y + 5))
    return rect

# Main loop
while True:
    screen.fill(WHITE)

    # Draw buttons
    block_btn = draw_button(10, 10, "Spawn Block")
    ball_btn = draw_button(10, 50, "Spawn Ball")

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            if block_btn.collidepoint(pos):
                create_block(random.randint(200, WIDTH - 100), 100)
            elif ball_btn.collidepoint(pos):
                create_ball(random.randint(200, WIDTH - 100), 100)
            else:
                drag_target = None
                for body, shape in reversed(objects):
                    if shape.point_query(pos).distance <= 0:
                        if body.body_type == pymunk.Body.DYNAMIC:
                            drag_target = body
                            mouse_body.position = pos
                            drag_joint = pymunk.PivotJoint(mouse_body, drag_target, (0, 0), (0, 0))
                            drag_joint.max_force = 5000
                            drag_joint.error_bias = 0.1 ** 60
                            space.add(drag_joint)
                            break

        elif event.type == pygame.MOUSEBUTTONUP:
            if drag_joint:
                space.remove(drag_joint)
                drag_joint = None
            drag_target = None

        elif event.type == pygame.KEYDOWN:
            if drag_target and drag_target.body_type == pymunk.Body.DYNAMIC:
                if event.key == pygame.K_a:
                    drag_target.angle -= 0.2
                elif event.key == pygame.K_d:
                    drag_target.angle += 0.2

    # Update mouse position
    mouse_pos = pygame.mouse.get_pos()
    mouse_body.position = mouse_pos

    # Step physics
    space.step(1/60.0)

    # Draw shapes manually
    for body, shape in objects:
        if isinstance(shape, pymunk.Poly):
            points = [body.local_to_world(v) for v in shape.get_vertices()]
            pygame.draw.polygon(screen, shape.color, points)
        elif isinstance(shape, pymunk.Circle):
            pygame.draw.circle(screen, shape.color, (int(body.position.x), int(body.position.y)), int(shape.radius))

    pygame.display.flip()
    clock.tick(60)
