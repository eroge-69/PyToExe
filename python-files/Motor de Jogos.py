import pygame
import pymunk
import pymunk.pygame_util
import sys
import math
import os

pygame.init()
screen = pygame.display.set_mode((1000, 600))
clock = pygame.time.Clock()
draw_options = pymunk.pygame_util.DrawOptions(screen)
font = pygame.font.SysFont(None, 24)

space = pymunk.Space()
space.gravity = (0, 900)
gravity_enabled = True
BREAK_FORCE = 800

# Chão estático
floor_body = pymunk.Body(body_type=pymunk.Body.STATIC)
floor_shape = pymunk.Segment(floor_body, (0, 580), (1000, 580), 5)
floor_shape.friction = 1.0
space.add(floor_body, floor_shape)

# Botões do menu (sem Reset)
buttons = {
    "Quadrado": pygame.Rect(10, 10, 80, 30),
    "Círculo": pygame.Rect(100, 10, 80, 30),
    "Triângulo": pygame.Rect(190, 10, 80, 30),
    "Retângulo": pygame.Rect(280, 10, 80, 30),
    "Hexágono": pygame.Rect(370, 10, 80, 30),
    "Boneco": pygame.Rect(460, 10, 80, 30),
    "Limpar": pygame.Rect(10, 50, 80, 30),
    "Sair": pygame.Rect(100, 50, 80, 30),
}

# Cores disponíveis
color_options = {
    "Vermelho": (255, 50, 50),
    "Verde": (50, 255, 50),
    "Azul": (50, 50, 255),
    "Amarelo": (255, 255, 50),
    "Branco": (255, 255, 255),
}

color_buttons = {}
x_color = 10
y_color = 90
for name in color_options:
    color_buttons[name] = pygame.Rect(x_color, y_color, 80, 30)
    y_color += 40

selected_shape = None
selected_color = (255, 255, 255)
objects = []
ragdoll_joints = []  # Guarda as juntas do boneco para remover depois

def create_poly_body(vertices, pos, color):
    mass = 1
    moment = pymunk.moment_for_poly(mass, vertices)
    body = pymunk.Body(mass, moment)
    body.position = pos
    shape = pymunk.Poly(body, vertices)
    shape.friction = 0.5
    shape.color = color + (255,)
    space.add(body, shape)
    return body

def create_square(pos, color):
    size = 50
    vertices = [(-size/2, -size/2), (-size/2, size/2), (size/2, size/2), (size/2, -size/2)]
    return create_poly_body(vertices, pos, color)

def create_rectangle(pos, color):
    width, height = 80, 40
    vertices = [(-width/2, -height/2), (-width/2, height/2), (width/2, height/2), (width/2, -height/2)]
    return create_poly_body(vertices, pos, color)

def create_triangle(pos, color):
    vertices = [(0, 30), (-25, -15), (25, -15)]
    return create_poly_body(vertices, pos, color)

def create_hexagon(pos, color):
    radius = 30
    vertices = []
    for i in range(6):
        angle = math.radians(60 * i)
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        vertices.append((x, y))
    return create_poly_body(vertices, pos, color)

def create_circle(pos, color):
    mass = 1
    radius = 25
    moment = pymunk.moment_for_circle(mass, 0, radius)
    body = pymunk.Body(mass, moment)
    body.position = pos
    shape = pymunk.Circle(body, radius)
    shape.friction = 0.5
    shape.color = color + (255,)
    space.add(body, shape)
    return body

def create_ragdoll(pos):
    global ragdoll_joints
    parts = {}
    parts['head'] = create_circle((pos[0], pos[1] - 60), (200, 200, 200))
    parts['torso'] = create_rectangle((pos[0], pos[1] - 20), (180, 180, 180))
    parts['left_arm'] = create_rectangle((pos[0] - 50, pos[1] - 20), (180, 180, 180))
    parts['right_arm'] = create_rectangle((pos[0] + 50, pos[1] - 20), (180, 180, 180))
    parts['left_leg'] = create_rectangle((pos[0] - 20, pos[1] + 30), (180, 180, 180))
    parts['right_leg'] = create_rectangle((pos[0] + 20, pos[1] + 30), (180, 180, 180))

    # Remove joints antigos, se houver
    for joint in ragdoll_joints:
        if joint in space.constraints:
            space.remove(joint)
    ragdoll_joints = []

    ragdoll_joints.append(pymunk.PinJoint(parts['head'], parts['torso'], (0, 10), (0, -40)))
    ragdoll_joints.append(pymunk.PinJoint(parts['left_arm'], parts['torso'], (30, 0), (-40, 0)))
    ragdoll_joints.append(pymunk.PinJoint(parts['right_arm'], parts['torso'], (-30, 0), (40, 0)))
    ragdoll_joints.append(pymunk.PinJoint(parts['left_leg'], parts['torso'], (0, -40), (-10, 40)))
    ragdoll_joints.append(pymunk.PinJoint(parts['right_leg'], parts['torso'], (0, -40), (10, 40)))

    for joint in ragdoll_joints:
        space.add(joint)

    for part in parts.values():
        objects.append(part)

dragging_body = None
mouse_joint = None
was_kinematic = False

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_g:
                gravity_enabled = not gravity_enabled
                space.gravity = (0, 900) if gravity_enabled else (0, 0)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pymunk.pygame_util.from_pygame(event.pos, screen)

            for name, rect in buttons.items():
                if rect.collidepoint(event.pos):
                    if name == "Limpar":
                        # Remove corpos e juntas
                        for body in objects:
                            for shape in body.shapes:
                                space.remove(shape)
                            space.remove(body)
                        objects.clear()
                        # Remove as juntas do ragdoll também
                        for joint in ragdoll_joints:
                            if joint in space.constraints:
                                space.remove(joint)
                        ragdoll_joints.clear()
                        selected_shape = None
                    elif name == "Sair":
                        pygame.quit()
                        sys.exit()
                    elif name == "Boneco":
                        create_ragdoll(mouse_pos)
                    else:
                        selected_shape = name
                    break

            for cname, crect in color_buttons.items():
                if crect.collidepoint(event.pos):
                    selected_color = color_options[cname]
                    break

            else:
                for body in reversed(objects):
                    shape_list = body.shapes
                    if any(s.point_query(mouse_pos).distance <= 0 for s in shape_list):
                        dragging_body = body
                        was_kinematic = False
                        if dragging_body.body_type != pymunk.Body.DYNAMIC:
                            was_kinematic = True
                            dragging_body.body_type = pymunk.Body.DYNAMIC
                        mouse_joint = pymunk.PivotJoint(space.static_body, dragging_body, mouse_pos)
                        mouse_joint.max_force = 50000
                        space.add(mouse_joint)
                        break

        elif event.type == pygame.MOUSEBUTTONUP:
            if mouse_joint is not None:
                space.remove(mouse_joint)
                mouse_joint = None
                if was_kinematic and dragging_body is not None:
                    dragging_body.body_type = pymunk.Body.KINEMATIC
                dragging_body = None

    if selected_shape and pygame.mouse.get_pressed()[0]:
        mouse_pos = pymunk.pygame_util.from_pygame(pygame.mouse.get_pos(), screen)
        if selected_shape == "Quadrado":
            obj = create_square(mouse_pos, selected_color)
        elif selected_shape == "Círculo":
            obj = create_circle(mouse_pos, selected_color)
        elif selected_shape == "Triângulo":
            obj = create_triangle(mouse_pos, selected_color)
        elif selected_shape == "Retângulo":
            obj = create_rectangle(mouse_pos, selected_color)
        elif selected_shape == "Hexágono":
            obj = create_hexagon(mouse_pos, selected_color)
        else:
            obj = None
        if obj:
            objects.append(obj)
        selected_shape = None

    # Fragmentação em triângulos vermelhos se bate forte no chão
    for body in objects[:]:
        vy = body.velocity.y
        if abs(vy) > BREAK_FORCE and body.position.y > 550:
            for shape in body.shapes:
                space.remove(shape)
            space.remove(body)
            objects.remove(body)
            for i in range(5):
                frag_pos = (body.position.x + i * 5 - 10, body.position.y - 10)
                vertices = [(0, 10), (-5, -5), (5, -5)]
                frag = create_poly_body(vertices, frag_pos, (255, 0, 0))
                frag.velocity = (body.velocity.x + i * 10 - 25, -abs(vy) / 2)
                objects.append(frag)

    if mouse_joint is not None and dragging_body is not None:
        new_mouse_pos = pymunk.pygame_util.from_pygame(pygame.mouse.get_pos(), screen)
        mouse_joint.anchor_a = new_mouse_pos

    screen.fill((30, 30, 30))

    # Desenha botões
    for name, rect in buttons.items():
        pygame.draw.rect(screen, (70, 70, 70), rect)
        text = font.render(name, True, (255, 255, 255))
        screen.blit(text, (rect.x + 5, rect.y + 7))

    # Desenha botões de cor
    for cname, crect in color_buttons.items():
        pygame.draw.rect(screen, color_options[cname], crect)
        text = font.render(cname, True, (0, 0, 0))
        screen.blit(text, (crect.x + 5, crect.y + 7))

    # Desenha chão
    pygame.draw.line(screen, (255, 255, 255), (0, 580), (1000, 580), 5)

    space.debug_draw(draw_options)

    space.step(1 / 60)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
