import math
import random
import sys
import pygame

# -----------------
# Game Settings
# -----------------
WIDTH, HEIGHT = 520, 760
FPS = 60
TITLE = "Car Runner — P. Ajay Kumar"

ROAD_MARGIN = 80
LANE_COUNT = 3
LANE_LINE_LENGTH = 40
LANE_LINE_GAP = 30

CAR_WIDTH, CAR_HEIGHT = 48, 90
CAR_COLOR = (230, 60, 60)
CAR_TURN_SPEED = 6

MAX_SPEED = 220.0
ACCEL_PER_SEC = 80.0
BRAKE_PER_SEC = 160.0
FRICTION_PER_SEC = 60.0
SPEED_TO_PX = 0.22

SPAWN_EVERY_METERS = 55
OBSTACLE_COLORS = [(40, 170, 255), (255, 210, 30), (190, 190, 190), (160, 90, 230)]
OBSTACLE_SPEED_FACTOR = 0.92

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_GRAY = (60, 60, 60)
GRASS = (40, 120, 40)
YELLOW = (255, 235, 59)
RED = (200, 0, 0)
GREEN = (0, 200, 0)

PLAYER_NAME = "P. Ajay Kumar"
WIN_SCORE = 1000  # win condition


# -----------------
# Helpers
# -----------------
def kmh_to_px_per_frame(speed_kmh: float) -> float:
    return speed_kmh * SPEED_TO_PX


def clamp(x, a, b):
    return max(a, min(b, x))


# -----------------
# Game Objects
# -----------------
class Car:
    def __init__(self, x, y, color=CAR_COLOR):
        self.x = x
        self.y = y
        self.w = CAR_WIDTH
        self.h = CAR_HEIGHT
        self.color = color

    @property
    def rect(self):
        return pygame.Rect(int(self.x - self.w / 2), int(self.y - self.h / 2), self.w, self.h)

    def draw(self, surf):
        r = self.rect
        pygame.draw.rect(surf, self.color, r, border_radius=8)
        tip = (r.centerx, r.top + 8)
        left = (r.left + 10, r.top + 26)
        right = (r.right - 10, r.top + 26)
        pygame.draw.polygon(surf, (240, 240, 240), [tip, left, right])
        pygame.draw.rect(surf, (255, 40, 40), (r.left + 8, r.bottom - 10, 12, 6), border_radius=2)
        pygame.draw.rect(surf, (255, 40, 40), (r.right - 20, r.bottom - 10, 12, 6), border_radius=2)


class Obstacle:
    def __init__(self, lane_x, y):
        self.w = CAR_WIDTH
        self.h = CAR_HEIGHT
        self.x = lane_x
        self.y = y
        self.color = random.choice(OBSTACLE_COLORS)

    @property
    def rect(self):
        return pygame.Rect(int(self.x - self.w / 2), int(self.y - self.h / 2), self.w, self.h)

    def draw(self, surf):
        pygame.draw.rect(surf, self.color, self.rect, border_radius=8)


# -----------------
# Drawing
# -----------------
def draw_speedometer(surf, speed_kmh):
    radius = 90
    cx, cy = WIDTH - radius - 16, HEIGHT - radius - 16
    pygame.draw.circle(surf, BLACK, (cx, cy), radius + 6)
    pygame.draw.circle(surf, DARK_GRAY, (cx, cy), radius + 4)
    pygame.draw.circle(surf, (30, 30, 30), (cx, cy), radius)

    start_angle = math.radians(135)
    end_angle = math.radians(45)
    span = end_angle - start_angle
    ticks = 11
    for i in range(ticks):
        t = i / (ticks - 1)
        ang = start_angle + t * span
        x1 = cx + int(math.cos(ang) * (radius - 14))
        y1 = cy + int(math.sin(ang) * (radius - 14))
        x2 = cx + int(math.cos(ang) * (radius - 2))
        y2 = cy + int(math.sin(ang) * (radius - 2))
        pygame.draw.line(surf, (180, 180, 180), (x1, y1), (x2, y2), 3)

    t = clamp(speed_kmh / MAX_SPEED, 0, 1)
    ang = start_angle + t * span
    nx = cx + int(math.cos(ang) * (radius - 18))
    ny = cy + int(math.sin(ang) * (radius - 18))
    pygame.draw.line(surf, (255, 70, 70), (cx, cy), (nx, ny), 4)
    pygame.draw.circle(surf, (230, 230, 230), (cx, cy), 6)

    font = pygame.font.SysFont("consolas", 20, bold=True)
    txt = font.render(f"{int(speed_kmh):3d} km/h", True, WHITE)
    surf.blit(txt, (cx - txt.get_width() // 2, cy - 12))


def draw_hud(surf, score, speed_kmh):
    font = pygame.font.SysFont("consolas", 22, bold=True)
    name_surf = font.render(PLAYER_NAME, True, WHITE)
    surf.blit(name_surf, (14, 12))
    score_surf = font.render(f"Score: {int(score):06d}", True, WHITE)
    surf.blit(score_surf, (WIDTH - score_surf.get_width() - 14, 12))
    draw_speedometer(surf, speed_kmh)


def draw_road_and_grass(surf, lane_xs, lane_lines):
    surf.fill(GRASS)
    road_rect = pygame.Rect(ROAD_MARGIN, 0, WIDTH - ROAD_MARGIN * 2, HEIGHT)
    pygame.draw.rect(surf, (70, 70, 70), road_rect)
    pygame.draw.rect(surf, (200, 200, 200), road_rect, 6, border_radius=8)
    for x in lane_xs[1:-1]:
        for y in lane_lines:
            pygame.draw.rect(surf, YELLOW, (x - 4, y, 8, LANE_LINE_LENGTH), border_radius=3)


# -----------------
# End Screen
# -----------------
def show_end_screen(screen, message, color, score):
    clock = pygame.time.Clock()
    big_font = pygame.font.SysFont("consolas", 50, bold=True)
    small_font = pygame.font.SysFont("consolas", 24)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

        screen.fill(BLACK)
        msg = big_font.render(message, True, color)
        score_text = small_font.render(f"Final Score: {int(score)}", True, WHITE)
        restart_text = small_font.render("Press R to Restart or Q to Quit", True, WHITE)

        screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2 - 80))
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2))
        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 50))

        pygame.display.flip()
        clock.tick(30)


# -----------------
# Game
# -----------------
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    road_left = ROAD_MARGIN
    road_right = WIDTH - ROAD_MARGIN
    lane_width = (road_right - road_left) / LANE_COUNT
    lane_centers = [road_left + lane_width * (i + 0.5) for i in range(LANE_COUNT)]

    player = Car(lane_centers[LANE_COUNT // 2], HEIGHT - 140)

    lane_lines = []
    y = -LANE_LINE_LENGTH
    while y < HEIGHT + LANE_LINE_LENGTH:
        lane_lines.append(y)
        y += LANE_LINE_LENGTH + LANE_LINE_GAP

    obstacles = []
    dist_since_spawn = 0.0
    speed_kmh = 0.0
    score = 0.0
    meters_travelled = 0.0

    while True:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()

        # --- Speed control ---
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            speed_kmh += ACCEL_PER_SEC * dt
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            speed_kmh -= BRAKE_PER_SEC * dt
        else:
            if speed_kmh > 0:
                speed_kmh -= FRICTION_PER_SEC * dt
        speed_kmh = clamp(speed_kmh, 0, MAX_SPEED)

        # Steering
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player.x -= CAR_TURN_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player.x += CAR_TURN_SPEED
        player.x = clamp(player.x, road_left + CAR_WIDTH / 2 + 8, road_right - CAR_WIDTH / 2 - 8)

        # World scroll
        scroll_px = kmh_to_px_per_frame(speed_kmh)
        for i in range(len(lane_lines)):
            lane_lines[i] += scroll_px
            if lane_lines[i] - LANE_LINE_LENGTH > HEIGHT:
                lane_lines[i] -= (LANE_LINE_LENGTH + LANE_LINE_GAP) * (len(lane_lines))

        for obs in obstacles:
            obs.y += scroll_px * OBSTACLE_SPEED_FACTOR
        obstacles = [o for o in obstacles if o.y - o.h / 2 < HEIGHT + 10]

        # Distance + score
        meters_this_frame = (speed_kmh * 1000 / 3600.0) * dt
        meters_travelled += meters_this_frame
        dist_since_spawn += meters_this_frame
        score += meters_this_frame * 1.8

        # Spawn obstacles
        if dist_since_spawn >= SPAWN_EVERY_METERS:
            dist_since_spawn = 0.0
            lane_idx = random.randrange(LANE_COUNT)
            x = lane_centers[lane_idx]
            y_spawn = -CAR_HEIGHT - random.randint(20, 160)
            obstacles.append(Obstacle(x, y_spawn))

        # Collision check
        for obs in obstacles:
            if player.rect.colliderect(obs.rect):
                restart = show_end_screen(screen, "GAME OVER", RED, score)
                if restart:
                    return main()

        # Win check
        if score >= WIN_SCORE:
            restart = show_end_screen(screen, "YOU WIN!", GREEN, score)
            if restart:
                return main()

        # --- Draw ---
        draw_road_and_grass(screen, lane_centers, lane_lines)
        for obs in obstacles:
            obs.draw(screen)
        player.draw(screen)
        draw_hud(screen, score, speed_kmh)
        pygame.display.flip()


if __name__ == "__main__":
    main()
