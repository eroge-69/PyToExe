import pygame
import asyncio
import platform
from collections import deque
import random
import time
import base64
import io

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maze Game with Dramatic Effects")

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# Player (ball) properties
player_pos = [50, 50]
player_speed = [5, 5]  # [x_speed, y_speed] for bounce
player_radius = 10
bounce_factor = 0.8  # Reduce speed slightly on bounce
speed_increase = 1.2  # Speed multiplier per bounce
max_speed = 15  # Maximum speed to prevent uncontrollable movement
ball_color = RED
pop_scale = 1.0  # For pop effect

# Trail properties
trail = deque(maxlen=50)  # Store up to 50 trail positions
trail_alpha_step = 255 / 50  # Fade alpha over trail length

# Goal properties (unreachable)
goal_pos = [700, 500]
goal_size = 20

# Maze walls (list of rectangles: [x, y, width, height, shrink_factor])
walls = [
    [0, 0, WIDTH, 10, 1.0],  # Top border
    [0, HEIGHT-10, WIDTH, 10, 1.0],  # Bottom border
    [0, 0, 10, HEIGHT, 1.0],  # Left border
    [WIDTH-10, 0, 10, HEIGHT, 1.0],  # Right border
    [100, 100, 200, 10, 1.0],  # Horizontal wall
    [400, 100, 10, 200, 1.0],  # Vertical wall
    [200, 200, 10, 200, 1.0],  # Vertical wall
    [300, 300, 200, 10, 1.0],  # Horizontal wall
    [600, 400, 10, 150, 1.0],  # Vertical wall
    # Walls around goal to make it unreachable
    [680, 480, 40, 10, 1.0],  # Top of goal
    [680, 510, 40, 10, 1.0],  # Bottom of goal
    [680, 480, 10, 40, 1.0],  # Left of goal
    [710, 480, 10, 40, 1.0],  # Right of goal
    # Additional walls for complexity
    [50, 150, 10, 150, 1.0],  # Vertical wall near start
    [150, 250, 150, 10, 1.0],  # Horizontal wall
    [350, 50, 10, 150, 1.0],   # Vertical wall
    [450, 350, 150, 10, 1.0],  # Horizontal wall
    [250, 450, 10, 100, 1.0],  # Vertical wall
    [550, 200, 100, 10, 1.0]   # Horizontal wall
]

# Load base64 image
base64_string = "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"
image_data = base64.b64decode(base64_string)
image_file = io.BytesIO(image_data)
image = pygame.image.load(image_file)

# Font for text
font = pygame.font.SysFont("arial", 48, bold=True)

# Game state
start_time = time.time()
effect_triggered = False
shake_time = 0
pop_time = 0
image_time = 0
background_color = WHITE
flash_time = 0
flash_state = True  # True for red, False for black

async def main():
    global player_pos, player_speed, trail, ball_color, pop_scale
    global effect_triggered, shake_time, pop_time, image_time, background_color
    global flash_time, flash_state
    running = True
    clock = pygame.time.Clock()

    def check_collision(new_pos):
        """Check if new player position collides with any wall and return collision details"""
        player_rect = pygame.Rect(new_pos[0] - player_radius, new_pos[1] - player_radius, player_radius * 2, player_radius * 2)
        for wall in walls:
            wall_rect = pygame.Rect(wall[0], wall[1], wall[2] * wall[4], wall[3] * wall[4])
            if player_rect.colliderect(wall_rect):
                # Determine collision side
                dx = (player_rect.centerx - wall_rect.centerx) / (wall_rect.width / 2)
                dy = (player_rect.centery - wall_rect.centery) / (wall_rect.height / 2)
                if abs(dx) > abs(dy):
                    return True, "horizontal"
                else:
                    return True, "vertical"
        return False, None

    while running:
        current_time = time.time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if not effect_triggered and current_time - start_time >= 6:
            effect_triggered = True
            ball_color = BLACK
            shake_time = current_time
            background_color = RED

        if effect_triggered:
            # Shake effect (1 second)
            if current_time - shake_time <= 1:
                shake_offset = [random.uniform(-3, 3), random.uniform(-3, 3)]
            else:
                shake_offset = [0, 0]
                # Pop effect (0.5 seconds)
                if pop_time == 0:
                    pop_time = current_time
                if current_time - pop_time <= 0.5:
                    pop_scale = 1.0 + (current_time - pop_time) * 2  # Scale up to 2x
                else:
                    pop_scale = 0  # Ball disappears
                    # Image and text appear after pop
                    if image_time == 0:
                        image_time = current_time
                    # Flash background red/black every 0.1 seconds
                    if current_time - flash_time >= 0.1:
                        flash_state = not flash_state
                        flash_time = current_time
                    background_color = RED if flash_state else BLACK
                    # Close game after 2 seconds of image
                    if current_time - image_time >= 2:
                        running = False
            # Melt walls
            for wall in walls:
                wall[4] = max(0, wall[4] - 0.02)  # Shrink walls over time
        else:
            shake_offset = [0, 0]

            # Get keyboard input
            keys = pygame.key.get_pressed()
            new_speed = player_speed.copy()
            if keys[pygame.K_LEFT]:
                new_speed[0] = -5
            if keys[pygame.K_RIGHT]:
                new_speed[0] = 5
            if keys[pygame.K_UP]:
                new_speed[1] = -5
            if keys[pygame.K_DOWN]:
                new_speed[1] = 5

            # Update position
            new_pos = [player_pos[0] + new_speed[0], player_pos[1] + new_speed[1]]

            # Check for collision
            collides, collision_type = check_collision(new_pos)
            if collides:
                # Bounce: reverse direction and increase speed
                if collision_type == "horizontal":
                    player_speed[0] = -player_speed[0] * bounce_factor * speed_increase
                    new_speed[0] = -new_speed[0] * bounce_factor * speed_increase
                    # Cap speed
                    if abs(player_speed[0]) > max_speed:
                        player_speed[0] = max_speed if player_speed[0] > 0 else -max_speed
                    if abs(new_speed[0]) > max_speed:
                        new_speed[0] = max_speed if new_speed[0] > 0 else -max_speed
                else:  # vertical
                    player_speed[1] = -player_speed[1] * bounce_factor * speed_increase
                    new_speed[1] = -new_speed[1] * bounce_factor * speed_increase
                    # Cap speed
                    if abs(player_speed[1]) > max_speed:
                        player_speed[1] = max_speed if player_speed[1] > 0 else -max_speed
                    if abs(new_speed[1]) > max_speed:
                        new_speed[1] = max_speed if new_speed[1] > 0 else -max_speed
                new_pos = player_pos.copy()  # Don't move into wall
            else:
                player_pos = new_pos
                player_speed = new_speed

            # Add current position to trail
            trail.append((player_pos[0], player_pos[1]))

        # Draw
        screen.fill(background_color)
        # Draw walls
        for wall in walls:
            pygame.draw.rect(screen, BLACK, (wall[0], wall[1], wall[2] * wall[4], wall[3] * wall[4]))
        # Draw goal (unreachable)
        pygame.draw.rect(screen, GREEN, (goal_pos[0], goal_pos[1], goal_size, goal_size))
        # Draw trail
        if pop_scale > 0:
            for i, pos in enumerate(trail):
                alpha = 255 - (i * trail_alpha_step)
                trail_surface = pygame.Surface((player_radius * 2, player_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(trail_surface, (255, 0, 0, int(alpha)), (player_radius, player_radius), player_radius)
                screen.blit(trail_surface, (pos[0] - player_radius, pos[1] - player_radius))
        # Draw player (ball)
        if pop_scale > 0:
            pygame.draw.circle(screen, ball_color, (int(player_pos[0] + shake_offset[0]), int(player_pos[1] + shake_offset[1])), int(player_radius * pop_scale))
        # Draw image and text after pop
        if pop_scale == 0 and image_time > 0:
            image_rect = image.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
            screen.blit(image, image_rect)
            text = font.render(". rip.pc. rip .files.", True, WHITE)
            text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
            screen.blit(text, text_rect)

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(1.0 / 60)

    pygame.quit()

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())