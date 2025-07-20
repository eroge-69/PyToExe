# astro_dodger.py
# A top-down space-themed dodging game.

import pygame
import random

# --- Initialization ---
pygame.init()
pygame.font.init()

# --- Constants and Configuration ---

# Screen
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PLAYER_COLOR = (0, 180, 255)  # A bright blue
ASTEROID_COLOR = (139, 145, 153) # Gray
POWERUP_COLOR = (46, 204, 113) # A vibrant green

# Game Fonts
SCORE_FONT = pygame.font.SysFont("dejavusans", 30)
GAME_OVER_FONT = pygame.font.SysFont("dejavusans", 75)
RESTART_FONT = pygame.font.SysFont("dejavusans", 40)

# Player Settings
PLAYER_SIZE = 40
PLAYER_SPEED = 8

# Asteroid Settings
ASTEROID_SIZE_MIN = 20
ASTEROID_SIZE_MAX = 50
ASTEROID_SPEED_MIN = 2
ASTEROID_SPEED_MAX = 6

# Starfield Settings
STAR_COUNT = 150
STAR_SPEED = 1

# Power-Up Settings
POWERUP_SIZE = 25
POWERUP_SPEED = 3
POWERUP_SPAWN_CHANCE = 0.002 # A small chance to spawn each frame
POWERUP_DURATION = 300 # In frames (5 seconds at 60 FPS)


# --- Game Window Setup ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Astro-Dodger")
clock = pygame.time.Clock()


# --- Game Classes ---

class Player:
    """Represents the player's spaceship."""
    def __init__(self):
        # Create a triangle shape for the player
        self.points = [
            (SCREEN_WIDTH / 2, SCREEN_HEIGHT - PLAYER_SIZE * 1.5), # Top point
            (SCREEN_WIDTH / 2 - PLAYER_SIZE / 2, SCREEN_HEIGHT - PLAYER_SIZE / 2), # Bottom-left
            (SCREEN_WIDTH / 2 + PLAYER_SIZE / 2, SCREEN_HEIGHT - PLAYER_SIZE / 2)  # Bottom-right
        ]
        # The hitbox is a rectangle that contains the triangle
        self.rect = pygame.Rect(
            SCREEN_WIDTH / 2 - PLAYER_SIZE / 2,
            SCREEN_HEIGHT - PLAYER_SIZE * 1.5,
            PLAYER_SIZE, PLAYER_SIZE
        )

    def move(self, dx):
        """Moves the player horizontally and keeps them within the screen bounds."""
        new_x = self.rect.x + dx
        if 0 <= new_x <= SCREEN_WIDTH - self.rect.width:
            self.rect.x = new_x
            # Update the points of the triangle as well
            for i in range(len(self.points)):
                self.points[i] = (self.points[i][0] + dx, self.points[i][1])

    def draw(self):
        """Draws the player's ship."""
        pygame.draw.polygon(screen, PLAYER_COLOR, self.points)


class Asteroid:
    """Represents a single falling asteroid."""
    def __init__(self):
        size = random.randint(ASTEROID_SIZE_MIN, ASTEROID_SIZE_MAX)
        start_x = random.randint(0, SCREEN_WIDTH - size)
        self.rect = pygame.Rect(start_x, -size, size, size)
        self.speed = random.randint(ASTEROID_SPEED_MIN, ASTEROID_SPEED_MAX)

    def update(self):
        """Moves the asteroid downwards."""
        self.rect.y += self.speed

    def draw(self):
        """Draws the asteroid."""
        pygame.draw.rect(screen, ASTEROID_COLOR, self.rect, border_radius=5)


class Star:
    """Represents a single star in the background starfield."""
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.size = random.randint(1, 3)
        self.speed = self.size # Smaller stars move slower for parallax effect

    def update(self):
        """Moves the star downwards and wraps it to the top if it goes off-screen."""
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            self.y = 0
            self.x = random.randint(0, SCREEN_WIDTH)

    def draw(self):
        """Draws the star."""
        pygame.draw.circle(screen, WHITE, (self.x, self.y), self.size)


class PowerUp:
    """Represents a shield power-up."""
    def __init__(self):
        start_x = random.randint(0, SCREEN_WIDTH - POWERUP_SIZE)
        self.rect = pygame.Rect(start_x, -POWERUP_SIZE, POWERUP_SIZE, POWERUP_SIZE)

    def update(self):
        """Moves the power-up downwards."""
        self.rect.y += POWERUP_SPEED

    def draw(self):
        """Draws the power-up."""
        pygame.draw.rect(screen, POWERUP_COLOR, self.rect, border_radius=8)
        # Draw a '+' symbol inside
        pygame.draw.line(screen, WHITE, (self.rect.centerx, self.rect.top + 5), (self.rect.centerx, self.rect.bottom - 5), 3)
        pygame.draw.line(screen, WHITE, (self.rect.left + 5, self.rect.centery), (self.rect.right - 5, self.rect.centery), 3)


# --- Main Game Function ---

def main_game():
    """The main function to run the game loop."""
    player = Player()
    asteroids = []
    stars = [Star() for _ in range(STAR_COUNT)]
    powerups = []

    # Game state variables
    running = True
    game_over = False
    score = 0
    asteroid_add_counter = 0
    asteroid_spawn_rate = 30  # Add a new asteroid every 30 frames initially

    shield_active = False
    shield_timer = 0

    while running:
        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r and game_over:
                # Restart the game by calling main_game() again
                main_game()
                return # Exit the current (finished) game loop

        if not game_over:
            # --- Player Movement ---
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                player.move(-PLAYER_SPEED)
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                player.move(PLAYER_SPEED)

            # --- Update Game Elements ---

            # Update stars
            for star in stars:
                star.update()

            # Add and update asteroids
            asteroid_add_counter += 1
            if asteroid_add_counter >= asteroid_spawn_rate:
                asteroid_add_counter = 0
                asteroids.append(Asteroid())
                # Increase difficulty by reducing spawn rate over time
                if asteroid_spawn_rate > 10:
                    asteroid_spawn_rate -= 0.1

            for asteroid in asteroids[:]:
                asteroid.update()
                # Remove asteroids that go off-screen
                if asteroid.rect.top > SCREEN_HEIGHT:
                    asteroids.remove(asteroid)
                    score += 1 # Increment score for successfully dodging

            # Add and update power-ups
            if random.random() < POWERUP_SPAWN_CHANCE and not shield_active and not powerups:
                powerups.append(PowerUp())

            for powerup in powerups[:]:
                powerup.update()
                if powerup.rect.top > SCREEN_HEIGHT:
                    powerups.remove(powerup)

            # --- Shield Timer ---
            if shield_active:
                shield_timer -= 1
                if shield_timer <= 0:
                    shield_active = False

            # --- Collision Detection ---
            # Player and asteroids
            for asteroid in asteroids:
                if player.rect.colliderect(asteroid.rect):
                    if not shield_active:
                        game_over = True
                    else:
                        # Shield deflects the asteroid
                        asteroids.remove(asteroid)
                        score += 5 # Bonus score for shield deflection

            # Player and power-ups
            for powerup in powerups[:]:
                if player.rect.colliderect(powerup.rect):
                    powerups.remove(powerup)
                    shield_active = True
                    shield_timer = POWERUP_DURATION


        # --- Drawing ---
        screen.fill(BLACK)

        # Draw stars
        for star in stars:
            star.draw()

        # Draw asteroids and power-ups
        for asteroid in asteroids:
            asteroid.draw()
        for powerup in powerups:
            powerup.draw()
            
        # Draw player
        player.draw()

        # Draw shield effect if active
        if shield_active:
            # Draw a semi-transparent circle around the player
            shield_surface = pygame.Surface((PLAYER_SIZE * 2, PLAYER_SIZE * 2), pygame.SRCALPHA)
            alpha = int(100 * (shield_timer / POWERUP_DURATION)) # Fade out effect
            pygame.draw.circle(shield_surface, (0, 255, 0, alpha), (PLAYER_SIZE, PLAYER_SIZE), PLAYER_SIZE)
            screen.blit(shield_surface, (player.rect.centerx - PLAYER_SIZE, player.rect.centery - PLAYER_SIZE))

        # Draw score
        score_text = SCORE_FONT.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        # Draw game over screen if applicable
        if game_over:
            game_over_text = GAME_OVER_FONT.render("GAME OVER", True, (255, 0, 0))
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 50))
            screen.blit(game_over_text, text_rect)
            
            restart_text = RESTART_FONT.render("Press 'R' to Restart", True, WHITE)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 30))
            screen.blit(restart_text, restart_rect)


        # --- Update Display ---
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


# --- Start the Game ---
if __name__ == "__main__":
    main_game()
