import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import random
import math

# Initialize pygame
pygame.init()
width, height = 800, 600
pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL)

# Set up perspective
gluPerspective(45, (width / height), 0.1, 50.0)
glTranslatef(0.0, 0.0, -5)

# Player variables
player_pos = [0, 0, 0]
player_rot = [0, 0]
player_speed = 0.1
mouse_sensitivity = 0.2

# Game objects
cubes = []
bullets = []
enemies = []
score = 0
game_over = False

# Create world
def create_world():
    global cubes
    # Ground
    for x in range(-10, 10):
        for z in range(-10, 10):
            cubes.append([x, -1, z, 0.5, 0.5, 0.5])  # Gray ground
    
    # Some obstacles
    for _ in range(20):
        x = random.randint(-8, 8)
        z = random.randint(-8, 8)
        if x != 0 and z != 0:  # Don't block player start
            cubes.append([x, 0, z, random.random(), random.random(), random.random()])

# Create enemies
def create_enemies(count):
    global enemies
    for _ in range(count):
        x = random.randint(-8, 8)
        z = random.randint(-8, 8)
        if abs(x) > 2 or abs(z) > 2:  # Don't spawn too close
            enemies.append([x, 0, z, 0.5, 0, 0, 1])  # Red enemies with health

# Draw cube
def draw_cube(x, y, z, r, g, b):
    glPushMatrix()
    glTranslatef(x, y, z)
    
    glBegin(GL_QUADS)
    glColor3f(r, g, b)
    
    # Front face
    glVertex3f(-0.5, -0.5, -0.5)
    glVertex3f(0.5, -0.5, -0.5)
    glVertex3f(0.5, 0.5, -0.5)
    glVertex3f(-0.5, 0.5, -0.5)
    
    # Back face
    glVertex3f(-0.5, -0.5, 0.5)
    glVertex3f(0.5, -0.5, 0.5)
    glVertex3f(0.5, 0.5, 0.5)
    glVertex3f(-0.5, 0.5, 0.5)
    
    # Left face
    glVertex3f(-0.5, -0.5, -0.5)
    glVertex3f(-0.5, 0.5, -0.5)
    glVertex3f(-0.5, 0.5, 0.5)
    glVertex3f(-0.5, -0.5, 0.5)
    
    # Right face
    glVertex3f(0.5, -0.5, -0.5)
    glVertex3f(0.5, -0.5, 0.5)
    glVertex3f(0.5, 0.5, 0.5)
    glVertex3f(0.5, 0.5, -0.5)
    
    # Top face
    glVertex3f(-0.5, 0.5, -0.5)
    glVertex3f(0.5, 0.5, -0.5)
    glVertex3f(0.5, 0.5, 0.5)
    glVertex3f(-0.5, 0.5, 0.5)
    
    # Bottom face
    glVertex3f(-0.5, -0.5, -0.5)
    glVertex3f(-0.5, -0.5, 0.5)
    glVertex3f(0.5, -0.5, 0.5)
    glVertex3f(0.5, -0.5, -0.5)
    
    glEnd()
    glPopMatrix()

# Draw bullet
def draw_bullet(x, y, z):
    glPushMatrix()
    glTranslatef(x, y, z)
    
    glBegin(GL_POINTS)
    glColor3f(1, 1, 0)  # Yellow bullets
    glVertex3f(0, 0, 0)
    glEnd()
    
    glPopMatrix()

# Handle player movement
def handle_movement():
    keys = pygame.key.get_pressed()
    
    # Forward/backward movement
    if keys[K_w]:
        player_pos[0] -= math.sin(math.radians(player_rot[1])) * player_speed
        player_pos[2] -= math.cos(math.radians(player_rot[1])) * player_speed
    if keys[K_s]:
        player_pos[0] += math.sin(math.radians(player_rot[1])) * player_speed
        player_pos[2] += math.cos(math.radians(player_rot[1])) * player_speed
    
    # Strafe movement
    if keys[K_a]:
        player_pos[0] -= math.sin(math.radians(player_rot[1] - 90)) * player_speed
        player_pos[2] -= math.cos(math.radians(player_rot[1] - 90)) * player_speed
    if keys[K_d]:
        player_pos[0] += math.sin(math.radians(player_rot[1] - 90)) * player_speed
        player_pos[2] += math.cos(math.radians(player_rot[1] - 90)) * player_speed
    
    # Jump (simple implementation)
    if keys[K_SPACE] and player_pos[1] = 0:
        player_pos[1] = 0.5
    
    # Apply gravity
    if player_pos[1] > 0:
        player_pos[1] -= 0.01
    else:
        player_pos[1] = 0

# Handle mouse look
def handle_mouse_look():
    rel_x, rel_y = pygame.mouse.get_rel()
    player_rot[0] -= rel_y * mouse_sensitivity
    player_rot[1] -= rel_x * mouse_sensitivity
    
    # Clamp vertical rotation
    if player_rot[0] > 90:
        player_rot[0] = 90
    if player_rot[0]  -90:
        player_rot[0] = -90

# Fire bullet
def fire_bullet():
    # Calculate direction based on player rotation
    dx = -math.sin(math.radians(player_rot[1]))
    dy = -math.sin(math.radians(player_rot[0]))
    dz = -math.cos(math.radians(player_rot[1]))
    
    # Start bullet slightly in front of player
    bullet_pos = [
        player_pos[0] + dx * 0.5,
        player_pos[1] + dy * 0.5 + 0.5,  # Slightly above
        player_pos[2] + dz * 0.5
    ]
    
    bullets.append([bullet_pos, [dx * 0.2, dy * 0.2, dz * 0.2], 100])  # [position, velocity, lifetime]

# Update bullets
def update_bullets():
    global bullets, enemies, score
    
    for bullet in bullets[:]:
        # Move bullet
        bullet[0][0] += bullet[1][0]
        bullet[0][1] += bullet[1][1]
        bullet[0][2] += bullet[1][2]
        bullet[2] -= 1
        
        # Check collision with enemies
        for enemy in enemies[:]:
            dist = math.sqrt(
                (bullet[0][0] - enemy[0])**2 +
                (bullet[0][1] - enemy[1])**2 +
                (bullet[0][2] - enemy[2])**2
            )
            
            if dist  0.8:  # Hit detection
                enemy[6] -= 1  # Reduce health
                if enemy[6] = 0:  # Enemy dead
                    enemies.remove(enemy)
                    score += 10
                    create_enemies(1)  # Spawn new enemy
                bullets.remove(bullet)
                break
        
        # Check collision with world
        for cube in cubes:
            if cube[1] > -0.5:  # Only check non-ground cubes
                if (abs(bullet[0][0] - cube[0])  0.6 and
                    abs(bullet[0][1] - cube[1])  0.6 and
                    abs(bullet[0][2] - cube[2])  0.6):
                    bullets.remove(bullet)
                    break
        
        # Remove if lifetime expired
        if bullet[2] = 0:
            bullets.remove(bullet)

# Update enemies
def update_enemies():
    global player_pos, game_over
    
    for enemy in enemies:
        # Simple AI: move toward player
        dx = player_pos[0] - enemy[0]
        dz = player_pos[2] - enemy[2]
        dist = math.sqrt(dx**2 + dz**2)
        
        if dist > 0:
            enemy[0] += dx / dist * 0.02
            enemy[2] += dz / dist * 0.02
        
        # Check if enemy reached player (game over)
        if dist  0.8:
            game_over = True

# Draw HUD
def draw_hud():
    # Switch to orthographic projection for HUD
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, width, height, 0, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Draw crosshair
    glColor3f(1, 1, 1)
    glBegin(GL_LINES)
    glVertex2f(width/2 - 10, height/2)
    glVertex2f(width/2 + 10, height/2)
    glVertex2f(width/2, height/2 - 10)
    glVertex2f(width/2, height/2 + 10)
    glEnd()
    
    # Draw score
    font = pygame.font.SysFont('Arial', 30)
    text = font.render(f"Score: {score}", True, (255, 255, 255))
    text_data = pygame.image.tostring(text, "RGBA", True)
    glRasterPos2f(10, 10)
    glDrawPixels(text.get_width(), text.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_data)
    
    # Draw game over message if needed
    if game_over:
        font = pygame.font.SysFont('Arial', 50)
        text = font.render("GAME OVER", True, (255, 0, 0))
        text_data = pygame.image.tostring(text, "RGBA", True)
        glRasterPos2f(width/2 - text.get_width()/2, height/2 - text.get_height()/2)
        glDrawPixels(text.get_width(), text.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_data)
    
    # Restore perspective projection
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()

# Main game loop
def main():
    global player_pos, player_rot, game_over, score
    
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)
    
    create_world()
    create_enemies(5)
    
    clock = pygame.time.Clock()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return
                if event.key == pygame.K_r and game_over:  # Restart game
                    player_pos = [0, 0, 0]
                    player_rot = [0, 0]
                    cubes.clear()
                    bullets.clear()
                    enemies.clear()
                    score = 0
                    game_over = False
                    create_world()
                    create_enemies(5)
            if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                if event.button == 1:  # Left mouse button
                    fire_bullet()
        
        if not game_over:
            handle_movement()
            handle_mouse_look()
            update_bullets()
            update_enemies()
        
        # Clear screen
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Set up camera
        glLoadIdentity()
        glRotatef(player_rot[0], 1, 0, 0)
        glRotatef(player_rot[1], 0, 1, 0)
        glTranslatef(-player_pos[0], -player_pos[1], -player_pos[2])
        
        # Draw world
        for cube in cubes:
            draw_cube(cube[0], cube[1], cube[2], cube[3], cube[4], cube[5])
        
        # Draw enemies
        for enemy in enemies:
            draw_cube(enemy[0], enemy[1], enemy[2], enemy[3], enemy[4], enemy[5])
        
        # Draw bullets
        for bullet in bullets:
            draw_bullet(bullet[0][0], bullet[0][1], bullet[0][2])
        
        # Draw HUD
        draw_hud()
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
