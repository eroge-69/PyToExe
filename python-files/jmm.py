import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Game constants
WIDTH, HEIGHT = 800, 900
GRAVITY = 0.4
FLAP_STRENGTH = -9
PIPE_SPEED = 4
PIPE_GAP = 170  # Changed from 200 to 170 as requested
PIPE_FREQUENCY = 1800  # milliseconds
GROUND_HEIGHT = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKY_BLUE = (135, 206, 235)
GROUND_COLOR = (139, 69, 19)
PIPE_COLORS = [
    (70, 180, 70),   # Green
    (80, 160, 80),   # Darker green
    (100, 200, 100)  # Brighter green
]

# Create the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird Premium")
clock = pygame.time.Clock()

# Load fonts
try:
    font_large = pygame.font.Font(None, 72)
    font_medium = pygame.font.Font(None, 48)
    font_small = pygame.font.Font(None, 36)
except:
    font_large = pygame.font.SysFont('Arial', 72, bold=True)
    font_medium = pygame.font.SysFont('Arial', 48)
    font_small = pygame.font.SysFont('Arial', 36)

class Bird:
    def __init__(self):
        self.x = 150
        self.y = HEIGHT // 2
        self.velocity = 0
        self.width = 60
        self.height = 50
        self.rotation = 0
        self.animation_count = 0
        self.wing_up = False

    def flap(self):
        self.velocity = FLAP_STRENGTH
        self.rotation = 15
        self.wing_up = True
        self.animation_count = 5

    def update(self):
        # Apply gravity
        self.velocity += GRAVITY
        self.y += self.velocity

        # Apply rotation
        self.rotation = max(-30, min(self.velocity * -3, 30))

        # Update wing animation
        if self.animation_count > 0:
            self.animation_count -= 1
        else:
            self.wing_up = False

        # Keep bird within screen bounds
        if self.y < 0:
            self.y = 0
            self.velocity = 0

    def draw(self):
        # Create bird surface
        bird_surface = pygame.Surface((self.width + 30, self.height + 20), pygame.SRCALPHA)
        
        # Body (main ellipse)
        pygame.draw.ellipse(bird_surface, (255, 215, 0), (10, 10, self.width, self.height - 10))
        
        # Head
        pygame.draw.circle(bird_surface, (255, 215, 0), (self.width - 5, self.height//2 - 5), 18)
        
        # Eye
        pygame.draw.circle(bird_surface, (255, 165, 0), (self.width + 3, self.height//2 - 8), 6)
        pygame.draw.circle(bird_surface, BLACK, (self.width + 5, self.height//2 - 8), 3)
        
        # Smaller beak
        beak_points = [
            (self.width + 10, self.height//2 - 4),  # Top point
            (self.width + 25, self.height//2),      # Front point
            (self.width + 10, self.height//2 + 4)   # Bottom point
        ]
        pygame.draw.polygon(bird_surface, (255, 140, 0), beak_points)
        pygame.draw.polygon(bird_surface, (200, 100, 0), beak_points, 1)  # Outline
        
        # Wings (animated)
        if self.wing_up:
            wing_points = [
                (self.width//2 + 10, self.height//2 + 5),
                (self.width//2 - 15, self.height//2 - 10),
                (self.width//2 - 5, self.height//2 - 15)
            ]
        else:
            wing_points = [
                (self.width//2 + 10, self.height//2 + 5),
                (self.width//2 - 15, self.height//2 + 10),
                (self.width//2 - 5, self.height//2 + 15)
            ]
        pygame.draw.polygon(bird_surface, (255, 200, 0), wing_points)
        
        # Rotate and draw
        rotated_bird = pygame.transform.rotate(bird_surface, self.rotation)
        screen.blit(rotated_bird, (self.x - rotated_bird.get_width()//2 + self.width//2, 
                                  self.y - rotated_bird.get_height()//2 + self.height//2))

    def get_mask(self):
        bird_surface = pygame.Surface((self.width + 30, self.height + 20), pygame.SRCALPHA)
        pygame.draw.ellipse(bird_surface, WHITE, (10, 10, self.width, self.height - 10))
        return pygame.mask.from_surface(bird_surface)

    def get_rect(self):
        return pygame.Rect(self.x - 10, self.y - 10, self.width + 20, self.height + 20)

class Pipe:
    def __init__(self):
        self.x = WIDTH
        self.gap_y = random.randint(250, HEIGHT - 250 - GROUND_HEIGHT)
        self.width = 80
        self.passed = False
        self.color = random.choice(PIPE_COLORS)
        self.pipe_top_height = self.gap_y - PIPE_GAP // 2
        self.pipe_bottom_y = self.gap_y + PIPE_GAP // 2

    def update(self):
        self.x -= PIPE_SPEED

    def draw(self):
        # Top pipe
        pygame.draw.rect(screen, self.color, (self.x, 0, self.width, self.pipe_top_height))
        pygame.draw.rect(screen, (0, 100, 0), (self.x-5, self.pipe_top_height-20, self.width+10, 20))
        
        # Bottom pipe
        bottom_height = HEIGHT - GROUND_HEIGHT - self.pipe_bottom_y
        pygame.draw.rect(screen, self.color, (self.x, self.pipe_bottom_y, self.width, bottom_height))
        pygame.draw.rect(screen, (0, 100, 0), (self.x-5, self.pipe_bottom_y, self.width+10, 20))

    def get_rects(self):
        bottom_height = HEIGHT - GROUND_HEIGHT - self.pipe_bottom_y
        return [
            pygame.Rect(self.x, 0, self.width, self.pipe_top_height),
            pygame.Rect(self.x, self.pipe_bottom_y, self.width, bottom_height)
        ]

def draw_background():
    # Gradient sky
    for y in range(HEIGHT):
        shade = min(235, 135 + y//8)
        pygame.draw.line(screen, (135, 206, shade), (0, y), (WIDTH, y))
    
    # Simple clouds
    for cloud in [(100, 100, 30), (300, 150, 40), (600, 80, 50)]:
        pygame.draw.ellipse(screen, (240, 240, 240, 200), (cloud[0], cloud[1], cloud[2]*2, cloud[2]))

def draw_ground():
    pygame.draw.rect(screen, GROUND_COLOR, (0, HEIGHT-GROUND_HEIGHT, WIDTH, GROUND_HEIGHT))
    # Ground texture
    for i in range(0, WIDTH, 40):
        pygame.draw.rect(screen, (160, 82, 45), (i, HEIGHT-GROUND_HEIGHT, 20, 10))
        pygame.draw.rect(screen, (160, 82, 45), (i+20, HEIGHT-GROUND_HEIGHT+10, 20, 10))

def game_over_screen(score, high_score):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    
    while True:
        game_over_text = font_large.render("GAME OVER", True, WHITE)
        score_text = font_medium.render(f"Score: {score}", True, WHITE)
        high_score_text = font_medium.render(f"High Score: {high_score}", True, WHITE)
        restart_text = font_small.render("Press R to restart", True, WHITE)
        quit_text = font_small.render("Press Q to quit", True, WHITE)

        screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//3))
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))
        screen.blit(high_score_text, (WIDTH//2 - high_score_text.get_width()//2, HEIGHT//2 + 60))
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 140))
        screen.blit(quit_text, (WIDTH//2 - quit_text.get_width()//2, HEIGHT//2 + 190))

        pygame.display.update()

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

def main():
    bird = Bird()
    pipes = []
    score = 0
    high_score = 0
    last_pipe = pygame.time.get_ticks()
    game_active = True

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and game_active:
                    bird.flap()

        # Draw background
        draw_background()

        if game_active:
            # Update bird
            bird.update()

            # Generate pipes
            time_now = pygame.time.get_ticks()
            if time_now - last_pipe > PIPE_FREQUENCY:
                pipes.append(Pipe())
                last_pipe = time_now

            # Update pipes
            for pipe in pipes[:]:
                pipe.update()

                # Collision detection
                bird_mask = bird.get_mask()
                for pipe_rect in pipe.get_rects():
                    pipe_mask = pygame.mask.from_surface(pygame.Surface((pipe_rect.width, pipe_rect.height)))
                    offset = (pipe_rect.x - bird.x, pipe_rect.y - bird.y)
                    if bird_mask.overlap(pipe_mask, offset):
                        game_active = False

                # Score counting
                if not pipe.passed and pipe.x + pipe.width < bird.x:
                    pipe.passed = True
                    score += 1
                    high_score = max(score, high_score)

                # Remove off-screen pipes
                if pipe.x < -pipe.width:
                    pipes.remove(pipe)

            # Ground collision
            if bird.y + bird.height > HEIGHT - GROUND_HEIGHT:
                game_active = False

            # Draw pipes
            for pipe in pipes:
                pipe.draw()

        # Draw bird
        bird.draw()
        
        # Draw ground
        draw_ground()

        # Display score
        if game_active:
            score_text = font_medium.render(str(score), True, WHITE)
            screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 80))

        # Game over handling
        if not game_active:
            if game_over_screen(score, high_score):
                # Reset game
                bird = Bird()
                pipes = []
                score = 0
                last_pipe = pygame.time.get_ticks()
                game_active = True
                continue
            else:
                break

        pygame.display.update()
        clock.tick(60)

if __name__ == "__main__":
    main()
