import pygame, random, sys

# --- Initialize ---
pygame.init()
WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pixel Raiders")

# --- Colors ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 215, 0)
RED = (200, 0, 0)

# --- Clock ---
FPS = 60
clock = pygame.time.Clock()

# --- Player ---
player_size = 40
player_speed = 5
player = pygame.Rect(WIDTH//2, HEIGHT//2, player_size, player_size)

# --- Coins ---
coins = []
for _ in range(10):
    x = random.randint(0, WIDTH-20)
    y = random.randint(0, HEIGHT-20)
    coins.append(pygame.Rect(x, y, 20, 20))

score = 0

# --- Instructions ---
instructions = [
    "How to Play:",
    "Use the arrow keys to move the red square.",
    "Collect the yellow coins to increase your score.",
    "Each coin is worth 10 points.",
    "The game ends when you close the window."
]

# --- Main Loop ---
while True:
    clock.tick(FPS)

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]: player.x -= player_speed
    if keys[pygame.K_RIGHT]: player.x += player_speed
    if keys[pygame.K_UP]: player.y -= player_speed
    if keys[pygame.K_DOWN]: player.y += player_speed

    # Collision with coins
    for coin in coins[:]:
        if player.colliderect(coin):
            coins.remove(coin)
            score += 10

    # Draw
    WIN.fill(BLACK)
    pygame.draw.rect(WIN, RED, player)
    for coin in coins:
        pygame.draw.rect(WIN, YELLOW, coin)

    # Score Display
    font = pygame.font.SysFont(None, 36)
    score_text = font.render(f"Score: {score}", True, WHITE)
    WIN.blit(score_text, (10, 10))

    # Draw Instructions on screen
    instr_font = pygame.font.SysFont(None, 24)
    for idx, line in enumerate(instructions):
        text_surface = instr_font.render(line, True, WHITE)
        WIN.blit(text_surface, (10, 50 + idx * 20))

    pygame.display.flip()
