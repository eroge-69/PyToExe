import pygame
import random
import time

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong - AI Opponent")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Paddle dimensions
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 100

# Ball properties
BALL_RADIUS = 10

# Clock
clock = pygame.time.Clock()

# Game variables
player_paddle = pygame.Rect(20, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)
ai_paddle = pygame.Rect(WIDTH - 20 - PADDLE_WIDTH, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)
ball = pygame.Rect(WIDTH//2 - BALL_RADIUS, HEIGHT//2 - BALL_RADIUS, BALL_RADIUS * 2, BALL_RADIUS * 2)

# Ball speed
ball_speed_x = 5
ball_speed_y = 3

# Game state
player_score = 0
ai_score = 0

# AI parameters
ai_speed = 5
ai_history = []
ai_history_size = 10

# Main game loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Player movement (up and down)
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP] and player_paddle.top > 0:
        player_paddle.y -= 5
    if keys[pygame.K_DOWN] and player_paddle.bottom < HEIGHT:
        player_paddle.y += 5

    # AI movement with learning
    # Track recent ball positions to improve AI
    ai_history.append(ball.y)
    if len(ai_history) > ai_history_size:
        ai_history.pop(0)
    
    # AI tries to predict where the ball will go based on history
    if ai_history:
        avg_ball_y = sum(ai_history) / len(ai_history)
        ai_paddle.y = max(0, min(HEIGHT - PADDLE_HEIGHT, avg_ball_y - 20))
    
    # Move AI paddle toward the ball (with learning)
    if ai_paddle.y < ball.y:
        ai_paddle.y += ai_speed * 0.1
    elif ai_paddle.y > ball.y:
        ai_paddle.y -= ai_speed * 0.1
    
    # Keep AI paddle within screen
    ai_paddle.y = max(0, min(HEIGHT - PADDLE_HEIGHT, ai_paddle.y))

    # Ball movement
    ball.x += ball_speed_x
    ball.y += ball_speed_y

    # Check for top and bottom collisions
    if ball.top <= 0 or ball.bottom >= HEIGHT:
        ball_speed_y = -ball_speed_y

    # Check for paddle collisions
    if ball.colliderect(player_paddle):
        # Ball hits player paddle
        ball_speed_x = -ball_speed_x
        ball_speed_y = random.uniform(-1, 1) * 2  # Random vertical speed
        
        # Add a small boost to the ball speed
        ball_speed_x += 0.5

    if ball.colliderect(ai_paddle):
        # Ball hits AI paddle
        ball_speed_x = -ball_speed_x
        ball_speed_y = random.uniform(-1, 1) * 2

    # Check for scoring
    if ball.left <= player_paddle.left:
        ai_score += 1
        ball = pygame.Rect(WIDTH//2 - BALL_RADIUS, HEIGHT//2 - BALL_RADIUS, BALL_RADIUS * 2, BALL_RADIUS * 2)
        ball_speed_x = 5
        ball_speed_y = 3

    if ball.right >= ai_paddle.right:
        player_score += 1
        ball = pygame.Rect(WIDTH//2 - BALL_RADIUS, HEIGHT//2 - BALL_RADIUS, BALL_RADIUS * 2, BALL_RADIUS * 2)
        ball_speed_x = 5
        ball_speed_y = 3

    # Draw everything
    screen.fill(BLACK)
    
    # Draw paddles
    pygame.draw.rect(screen, WHITE, player_paddle)
    pygame.draw.rect(screen, WHITE, ai_paddle)
    
    # Draw ball
    pygame.draw.ellipse(screen, WHITE, ball)
    
    # Draw center line
    pygame.draw.line(screen, WHITE, (WIDTH//2, 0), (WIDTH//2, HEIGHT), 2)
    
    # Display scores
    font = pygame.font.Font(None, 36)
    player_text = font.render(f"Player: {player_score}", True, WHITE)
    ai_text = font.render(f"AI: {ai_score}", True, WHITE)
    screen.blit(player_text, (WIDTH//4 - 100, 20))
    screen.blit(ai_text, (3*WIDTH//4 - 100, 20))
    
    # Draw AI learning info
    if ai_history:
        ai_info = font.render(f"AI Learning: {len(ai_history)}", True, RED)
        screen.blit(ai_info, (WIDTH - 150, 50))
    
    # Update display
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
