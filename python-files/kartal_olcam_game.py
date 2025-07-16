import pygame
import random

pygame.init()

# Ekran boyutu
WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Kartal Olcam")
clock = pygame.time.Clock()

# Renkler
WHITE = (255, 255, 255)
BLUE = (0, 150, 255)
GREEN = (0, 200, 0)
BLACK = (0, 0, 0)

# Kuş (kartal)
bird_x, bird_y = 50, HEIGHT//2
bird_radius = 20
bird_velocity = 0
gravity = 0.5
jump_strength = -8

# Borular
pipe_width = 60
pipe_gap = 150
pipes = []
pipe_speed = 3

# Skor ve durum
score = 0
game_over = False
font = pygame.font.SysFont(None, 40)

# Ses efektleri
death_sound = pygame.mixer.Sound("death_sound.wav")
pass_sound = pygame.mixer.Sound("pass_sound.wav")

def create_pipe():
    y = random.randint(100, HEIGHT - 200)
    return {'x': WIDTH, 'top': y - pipe_gap//2, 'bottom': y + pipe_gap//2}

pipes.append(create_pipe())

running = True
while running:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if not game_over and (event.key == pygame.K_SPACE or event.key == pygame.K_UP):
                bird_velocity = jump_strength
            if game_over and event.key == pygame.K_r:
                bird_x, bird_y = 50, HEIGHT//2
                bird_velocity = 0
                pipes = [create_pipe()]
                score = 0
                game_over = False

    if not game_over:
        bird_velocity += gravity
        bird_y += bird_velocity

        # Boruları hareket ettir
        for pipe in pipes:
            pipe['x'] -= pipe_speed

        # Yeni boru ekle
        if pipes[-1]['x'] < WIDTH - 200:
            pipes.append(create_pipe())

        # Borudan geçme kontrolü ve skor
        if pipes[0]['x'] + pipe_width < bird_x and not pipes[0].get('scored'):
            score += 1
            pipes[0]['scored'] = True
            pass_sound.play()

        # Ekrandan çıkan boruyu sil
        if pipes[0]['x'] < -pipe_width:
            pipes.pop(0)

        # Çarpışma kontrolü
        for pipe in pipes:
            if bird_x + bird_radius > pipe['x'] and bird_x - bird_radius < pipe['x'] + pipe_width:
                if bird_y - bird_radius < pipe['top'] or bird_y + bird_radius > pipe['bottom']:
                    game_over = True
                    death_sound.play()
        if bird_y - bird_radius < 0 or bird_y + bird_radius > HEIGHT:
            game_over = True
            death_sound.play()

    # Ekranı çiz
    screen.fill(BLUE)

    # Borular
    for pipe in pipes:
        pygame.draw.rect(screen, GREEN, (pipe['x'], 0, pipe_width, pipe['top']))
        pygame.draw.rect(screen, GREEN, (pipe['x'], pipe['bottom'], pipe_width, HEIGHT - pipe['bottom']))

    # Kartal (kuş)
    pygame.draw.circle(screen, BLACK, (int(bird_x), int(bird_y)), bird_radius)

    # Skor
    score_text = font.render(f"Skor: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    if game_over:
        over_text = font.render("Hay aksi, bir şeyler ters gitti! (R ile yeniden)", True, WHITE)
        screen.blit(over_text, (20, HEIGHT//2 - 30))

    pygame.display.flip()

pygame.quit()
