import pygame
import math
import random
from datetime import datetime

pygame.init()
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Parabola Day-Night Clock")

# Fonts
font_big = pygame.font.SysFont("Arial", 120, bold=True)
font_medium = pygame.font.SysFont("Arial", 50, bold=True)
font_small = pygame.font.SysFont("Arial", 40, bold=True)
font_location = pygame.font.SysFont("Arial", 35, bold=True)

clock = pygame.time.Clock()

# Sun/Moon timings
SUNRISE, SUNSET = 6, 18
MOONRISE, MOONSET = 18, 6

# Stars
stars = [(random.randint(50, WIDTH-50), random.randint(50, HEIGHT//2)) for _ in range(80)]

# Clouds (x, y, speed)
clouds = [[random.randint(0, WIDTH), random.randint(50, HEIGHT//2), random.uniform(0.3, 1.0)] for _ in range(10)]

# -----------------------------------------------------
def get_parabola_position(now, rise, set_):
    """Return x,y along a parabola arc from rise→set_"""
    hour = now.hour + now.minute / 60.0
    if rise < set_:  # normal span
        t = (hour - rise) / (set_ - rise)
    else:  # spans midnight
        if hour >= rise:
            t = (hour - rise) / (24 - rise + set_)
        else:
            t = (hour + 24 - rise) / (24 - rise + set_)
    t = max(0, min(1, t))

    x = int(200 + t * (WIDTH - 400))
    mid = WIDTH // 2
    scale = (WIDTH - 400) // 2
    norm_x = (x - mid) / scale
    y = HEIGHT // 2 + 200
    y -= (1 - norm_x**2) * 200  # parabola
    return x, int(y)

def get_bg_and_text_colors(now):
    hour = now.hour
    if 5 <= hour < 9:  # Morning
        bg = (255, 180, 100)
        text = (0, 0, 0)
    elif 9 <= hour < 16:  # Noon
        bg = (135, 206, 235)
        text = (0, 0, 0)
    elif 16 <= hour < 19:  # Evening
        bg = (255, 140, 80)
        text = (0, 0, 0)
    else:  # Night
        bg = (10, 10, 30)
        text = (255, 255, 220)
    return bg, text

def draw_background(now, bg_color):
    screen.fill(bg_color)
    hour = now.hour

    # Night stars
    if hour >= 19 or hour < 6:
        for (sx, sy) in stars:
            if random.random() > 0.5:  # twinkle
                pygame.draw.circle(screen, (255, 255, 200), (sx, sy), 2)

    # Move + draw clouds
    if 6 <= hour < 19:
        for cloud in clouds:
            cloud[0] += cloud[2]  # move cloud by its speed
            if cloud[0] > WIDTH + 150:
                cloud[0] = -150  # wrap around
                cloud[1] = random.randint(50, HEIGHT//2)
            cx, cy = int(cloud[0]), int(cloud[1])
            pygame.draw.ellipse(screen, (255, 255, 255), (cx, cy, 120, 60))
            pygame.draw.ellipse(screen, (255, 255, 255), (cx+40, cy-20, 100, 80))

def draw_parabola_path(text_color):
    """Draw the parabola path with Sunrise, Noon, Sunset labels"""
    points = []
    mid = WIDTH // 2
    scale = (WIDTH - 400) // 2
    for px in range(200, WIDTH-200, 10):  # smooth curve
        norm_x = (px - mid) / scale
        y = HEIGHT // 2 + 200 - (1 - norm_x**2) * 200
        points.append((px, int(y)))
    if len(points) > 1:
        pygame.draw.lines(screen, (0, 0, 0), False, points, 2)

    # Add labels: Sunrise, Noon, Sunset
    sunrise_pos = (200, HEIGHT//2 + 200)
    noon_pos = (WIDTH//2, HEIGHT//2 - 0)  # top of parabola
    sunset_pos = (WIDTH-200, HEIGHT//2 + 200)

    sunrise_txt = font_small.render("6:00 AM", True, text_color)
    noon_txt = font_small.render("12:00 PM", True, text_color)
    sunset_txt = font_small.render("6:00 PM", True, text_color)

    screen.blit(sunrise_txt, (sunrise_pos[0] - 40, sunrise_pos[1] + 20))
    screen.blit(noon_txt, (noon_pos[0] - 70, noon_pos[1] - 60))
    screen.blit(sunset_txt, (sunset_pos[0] - 60, sunset_pos[1] + 20))

def draw_clock(now, text_color):
    # Location tag at TOP
    location_text = "Vijayawada, Gulabi Thota, Saibaba Street, 520003, AP"
    location_surface = font_location.render(location_text, True, text_color)
    location_rect = location_surface.get_rect(center=(WIDTH//2, 50))
    screen.blit(location_surface, location_rect)

    # Time + Date
    time_str = now.strftime("%I:%M:%S %p")
    date_str = now.strftime("%A, %d %b %Y")
    time_surface = font_big.render(time_str, True, text_color)
    date_surface = font_medium.render(date_str, True, text_color)
    time_rect = time_surface.get_rect(center=(WIDTH//2, HEIGHT//4))
    date_rect = date_surface.get_rect(center=(WIDTH//2, HEIGHT//4 + 120))
    screen.blit(time_surface, time_rect)
    screen.blit(date_surface, date_rect)

def draw_sun_moon(now, text_color):
    draw_parabola_path(text_color)  # arc path + labels
    if SUNRISE <= now.hour < SUNSET:  # Sun
        x, y = get_parabola_position(now, SUNRISE, SUNSET)
        pygame.draw.circle(screen, (255, 220, 0), (x, y), 30)
    else:  # Moon
        x, y = get_parabola_position(now, MOONRISE, MOONSET)
        pygame.draw.circle(screen, (220, 220, 255), (x, y), 25)

def main():
    running = True
    while running:
        now = datetime.now()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False

        bg_color, text_color = get_bg_and_text_colors(now)
        draw_background(now, bg_color)
        draw_clock(now, text_color)
        draw_sun_moon(now, text_color)

        pygame.display.flip()
        clock.tick(30)
    pygame.quit()

if __name__ == "__main__":
    main()
