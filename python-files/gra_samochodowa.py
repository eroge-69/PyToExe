import pygame
import random

# Inicjalizacja Pygame
pygame.init()

# Rozmiar okna
WIDTH, HEIGHT = 800, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bajerowa Gra Samochodowa")

# Kolory
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# FPS
clock = pygame.time.Clock()
FPS = 60

# Samochód gracza
car_img = pygame.image.load("car.png")  # Wstaw swoją grafikę PNG samochodu
car_width = 50
car_height = 100
car_x = WIDTH//2 - car_width//2
car_y = HEIGHT - car_height - 20
car_vel = 7

# Przeszkody
obstacle_width = 50
obstacle_height = 100
obstacles = []
obstacle_vel = 5
spawn_delay = 1500  # ms
last_spawn = pygame.time.get_ticks()

# Wynik
score = 0
font = pygame.font.SysFont("Arial", 30)

# Tło (przewijanie)
bg = pygame.image.load("road.png")  # Wstaw swoją grafikę drogi
bg_y = 0
bg_vel = 5

# Funkcja rysowania
def draw_window():
    global bg_y
    # Rysuj tło
    win.blit(bg, (0, bg_y))
    win.blit(bg, (0, bg_y - HEIGHT))
    # Przesuwanie tła
    bg_y += bg_vel
    if bg_y >= HEIGHT:
        bg_y = 0

    # Rysuj samochód
    win.blit(car_img, (car_x, car_y))

    # Rysuj przeszkody
    for obs in obstacles:
        pygame.draw.rect(win, (255,0,0), obs)

    # Wynik
    score_text = font.render(f"Wynik: {score}", True, WHITE)
    win.blit(score_text, (10,10))

    pygame.display.update()

# Główna pętla gry
run = True
while run:
    clock.tick(FPS)
    draw_window()

    # Sprawdzenie zdarzeń
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    # Sterowanie
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and car_x - car_vel > 0:
        car_x -= car_vel
    if keys[pygame.K_RIGHT] and car_x + car_vel + car_width < WIDTH:
        car_x += car_vel
    if keys[pygame.K_UP] and car_y - car_vel > 0:
        car_y -= car_vel
    if keys[pygame.K_DOWN] and car_y + car_vel + car_height < HEIGHT:
        car_y += car_vel

    # Tworzenie przeszkód
    now = pygame.time.get_ticks()
    if now - last_spawn > spawn_delay:
        obs_x = random.randint(0, WIDTH - obstacle_width)
        obs_y = -obstacle_height
        obstacles.append(pygame.Rect(obs_x, obs_y, obstacle_width, obstacle_height))
        last_spawn = now

    # Ruch przeszkód i kolizje
    for obs in obstacles[:]:
        obs.y += obstacle_vel
        if obs.y > HEIGHT:
            obstacles.remove(obs)
            score += 1  # punkt za przejechaną przeszkodę
        if obs.colliderect(pygame.Rect(car_x, car_y, car_width, car_height)):
            run = False  # Koniec gry przy kolizji

pygame.quit()
