import pygame
import random
import math

pygame.init()

info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Balls with Size & Spawn Control")

# Initial parameters
BASE_BALL_RADIUS = int(HEIGHT * 0.05)
ball_radius = BASE_BALL_RADIUS

FPS = 60
SPEED_BOOST = 1.03
MAX_SPEED = 10
SPAWN_COOLDOWN_MS = 3000

COLOR_PALETTE = [
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (255, 255, 0),
    (255, 0, 255),
    (0, 255, 255),
]

size_reduced = False
speed_scale = 1.0

def random_color():
    return random.choice(COLOR_PALETTE)

def velocity_toward_center(x, y):
    cx, cy = WIDTH / 2, HEIGHT / 2
    angle = math.atan2(cy - y, cx - x)
    speed = random.uniform(2, 5) * speed_scale
    return speed * math.cos(angle), speed * math.sin(angle)

def random_velocity():
    angle = random.uniform(0, 2 * math.pi)
    speed = random.uniform(2, 5) * speed_scale
    return speed * math.cos(angle), speed * math.sin(angle)

class Ball:
    def __init__(self, x, y, dx=None, dy=None, last_spawn_time=None):
        self.x = x
        self.y = y
        self.dx, self.dy = dx or 0, dy or 0
        if dx is None or dy is None:
            self.dx, self.dy = velocity_toward_center(x, y)
        self.color = random_color()
        self.last_spawn_time = last_spawn_time or pygame.time.get_ticks()

    def move(self):
        self.x += self.dx
        self.y += self.dy

        bounced = False
        if self.x - ball_radius < 0:
            self.x = ball_radius
            self.dx *= -1
            bounced = True
        elif self.x + ball_radius > WIDTH:
            self.x = WIDTH - ball_radius
            self.dx *= -1
            bounced = True

        if self.y - ball_radius < 0:
            self.y = ball_radius
            self.dy *= -1
            bounced = True
        elif self.y + ball_radius > HEIGHT:
            self.y = HEIGHT - ball_radius
            self.dy *= -1
            bounced = True

        if bounced:
            self.boost_speed()
            self.color = random_color()

    def boost_speed(self):
        speed = math.hypot(self.dx, self.dy)
        if speed < MAX_SPEED * speed_scale:
            self.dx *= SPEED_BOOST
            self.dy *= SPEED_BOOST

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), ball_radius)

    def collide(self, other):
        dist = math.hypot(self.x - other.x, self.y - other.y)
        return dist < ball_radius * 2

    def can_spawn(self):
        return pygame.time.get_ticks() - self.last_spawn_time >= SPAWN_COOLDOWN_MS

    def resolve_collision(self, other):
        nx = other.x - self.x
        ny = other.y - self.y
        dist = math.hypot(nx, ny)
        if dist == 0:
            dist = 0.1

        min_dist = ball_radius * 2
        overlap = min_dist - dist
        if overlap > 0:
            nx /= dist
            ny /= dist
            self.x -= nx * overlap / 2
            self.y -= ny * overlap / 2
            other.x += nx * overlap / 2
            other.y += ny * overlap / 2

            tx = -ny
            ty = nx

            dpTan1 = self.dx * tx + self.dy * ty
            dpTan2 = other.dx * tx + other.dy * ty

            dpNorm1 = self.dx * nx + self.dy * ny
            dpNorm2 = other.dx * nx + other.dy * ny

            self.dx = tx * dpTan1 + nx * dpNorm2
            self.dy = ty * dpTan1 + ny * dpNorm2
            other.dx = tx * dpTan2 + nx * dpNorm1
            other.dy = ty * dpTan2 + ny * dpNorm1

class PendingSpawn:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.created_time = pygame.time.get_ticks()

    def draw_marker(self, screen):
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), 10, 2)

    def is_area_clear(self, balls):
        clearance_radius = ball_radius * 2.5
        for b in balls:
            dist = math.hypot(b.x - self.x, b.y - self.y)
            if dist < clearance_radius:
                return False
        return True

balls = [
    Ball(ball_radius, ball_radius),
    Ball(WIDTH - ball_radius, ball_radius),
    Ball(ball_radius, HEIGHT - ball_radius),
    Ball(WIDTH - ball_radius, HEIGHT - ball_radius),
]

pending_spawns = []
clock = pygame.time.Clock()
running = True

def check_area_coverage(balls):
    total_area = WIDTH * HEIGHT
    square_side = ball_radius * 2
    ball_area_sum = len(balls) * (square_side ** 2)
    return (ball_area_sum / total_area) >= 0.5

while running:
    screen.fill((30, 30, 30))
    now = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT or (
            event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
        ):
            running = False

    # Only remove balls that are *completely* stopped
    balls = [b for b in balls if not (b.dx == 0 and b.dy == 0)]

    if not size_reduced and check_area_coverage(balls):
        size_reduced = True
        ball_radius = BASE_BALL_RADIUS // 2
        speed_scale = 0.1
        for b in balls:
            b.dx *= speed_scale
            b.dy *= speed_scale

    for ball in balls:
        ball.move()

    handled_pairs = set()
    for i in range(len(balls)):
        for j in range(i + 1, len(balls)):
            b1, b2 = balls[i], balls[j]
            if b1.collide(b2):
                pair = (min(i, j), max(i, j))
                if pair not in handled_pairs:
                    handled_pairs.add(pair)
                    if b1.color == b2.color and b1.can_spawn() and b2.can_spawn():
                        pending_spawns.append(PendingSpawn(b1.x, b1.y))
                        b1.last_spawn_time = now
                        b2.last_spawn_time = now
                    b1.resolve_collision(b2)
                    b1.color = random_color()
                    b2.color = random_color()

    for spawn in pending_spawns[:]:
        if now - spawn.created_time > 5000:
            pending_spawns.remove(spawn)
            continue

        if spawn.is_area_clear(balls):
            dx, dy = random_velocity()
            x = max(ball_radius, min(WIDTH - ball_radius, spawn.x))
            y = max(ball_radius, min(HEIGHT - ball_radius, spawn.y))
            balls.append(Ball(x, y, dx, dy, last_spawn_time=now))
            pending_spawns.remove(spawn)
        else:
            spawn.draw_marker(screen)

    for ball in balls:
        ball.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()