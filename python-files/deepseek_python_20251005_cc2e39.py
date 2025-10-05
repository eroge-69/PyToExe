import pygame
import pygame.gfxdraw
import math
import random
import sys
import os
from OpenGL.GL import *
from OpenGL.GLU import *

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Game constants
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 100, 255)
YELLOW = (255, 255, 50)
PURPLE = (180, 70, 200)
GRAY = (100, 100, 100)
DARK_GREEN = (20, 100, 20)
BROWN = (139, 69, 19)

class Player:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.z = 0
        self.angle = 0
        self.health = 100
        self.ammo = 12
        self.alive = True
        self.speed = 0.1
        self.height = 1.5
        
    def move_forward(self):
        self.x += math.sin(math.radians(self.angle)) * self.speed
        self.z += math.cos(math.radians(self.angle)) * self.speed
        
    def move_backward(self):
        self.x -= math.sin(math.radians(self.angle)) * self.speed
        self.z -= math.cos(math.radians(self.angle)) * self.speed
        
    def move_left(self):
        self.x += math.sin(math.radians(self.angle - 90)) * self.speed
        self.z += math.cos(math.radians(self.angle - 90)) * self.speed
        
    def move_right(self):
        self.x += math.sin(math.radians(self.angle + 90)) * self.speed
        self.z += math.cos(math.radians(self.angle + 90)) * self.speed
        
    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, self.y + self.height, self.z)
        glColor3f(0.2, 0.2, 0.8)
        glutSolidCube(0.5)
        glPopMatrix()

class Enemy:
    def __init__(self, x, z, enemy_type="soldier"):
        self.x = x
        self.y = 0
        self.z = z
        self.health = 100
        self.alive = True
        self.angle = random.uniform(0, 360)
        self.speed = random.uniform(0.02, 0.05)
        self.height = 1.5
        self.type = enemy_type
        self.shoot_cooldown = 0
        self.detection_range = 15 if enemy_type == "soldier" else 25
        self.attack_range = 10 if enemy_type == "soldier" else 20
        
        # Different colors for different enemy types
        if enemy_type == "soldier":
            self.color = (0.8, 0.2, 0.2)
        else:  # sniper
            self.color = (0.6, 0.1, 0.1)
            
    def update(self, player):
        if not self.alive:
            return
            
        # Calculate distance to player
        dx = player.x - self.x
        dz = player.z - self.z
        distance = math.sqrt(dx*dx + dz*dz)
        
        # Update shoot cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
            
        # If player is within detection range, move towards player
        if distance < self.detection_range:
            # Calculate angle to player
            self.angle = math.degrees(math.atan2(dx, dz))
            
            # Move towards player if not too close
            if distance > 2:
                self.x += math.sin(math.radians(self.angle)) * self.speed
                self.z += math.cos(math.radians(self.angle)) * self.speed
                
            # Shoot at player if in range and cooldown is ready
            if distance < self.attack_range and self.shoot_cooldown <= 0:
                self.shoot_cooldown = 60  # 1 second cooldown at 60 FPS
                return True  # Signal that enemy is shooting
                
        else:
            # Random wandering
            self.angle += random.uniform(-5, 5)
            self.x += math.sin(math.radians(self.angle)) * self.speed * 0.5
            self.z += math.cos(math.radians(self.angle)) * self.speed * 0.5
            
        return False
        
    def draw(self):
        if not self.alive:
            return
            
        glPushMatrix()
        glTranslatef(self.x, self.y + self.height/2, self.z)
        glRotatef(self.angle, 0, 1, 0)
        glColor3f(*self.color)
        
        # Draw enemy body
        glutSolidCube(0.8)
        
        # Draw gun
        glPushMatrix()
        glTranslatef(0.3, 0, 0.4)
        glColor3f(0.3, 0.3, 0.3)
        glutSolidCube(0.2)
        glPopMatrix()
        
        glPopMatrix()

class Bullet:
    def __init__(self, x, z, angle, speed, is_player_bullet=True):
        self.x = x
        self.y = 1.2 if is_player_bullet else 1.0
        self.z = z
        self.angle = angle
        self.speed = speed
        self.is_player_bullet = is_player_bullet
        self.distance = 0
        self.max_distance = 50
        
    def update(self):
        self.x += math.sin(math.radians(self.angle)) * self.speed
        self.z += math.cos(math.radians(self.angle)) * self.speed
        self.distance += self.speed
        
        return self.distance < self.max_distance
        
    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        if self.is_player_bullet:
            glColor3f(1.0, 1.0, 0.0)  # Yellow for player bullets
        else:
            glColor3f(1.0, 0.0, 0.0)  # Red for enemy bullets
        glutSolidSphere(0.1, 8, 8)
        glPopMatrix()

class AmmoBox:
    def __init__(self, x, z):
        self.x = x
        self.y = 0.5
        self.z = z
        self.collected = False
        self.rotation = 0
        
    def update(self):
        self.rotation += 1
        
    def draw(self):
        if self.collected:
            return
            
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        glRotatef(self.rotation, 0, 1, 0)
        glColor3f(0.2, 0.8, 0.2)
        glutSolidCube(0.8)
        glPopMatrix()

class Obstacle:
    def __init__(self, x, z, width, height, depth):
        self.x = x
        self.y = height / 2
        self.z = z
        self.width = width
        self.height = height
        self.depth = depth
        
    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        glColor3f(0.5, 0.5, 0.5)
        glutSolidCube(self.width)
        glPopMatrix()

class EscapePoint:
    def __init__(self, x, z):
        self.x = x
        self.y = 0.2
        self.z = z
        self.radius = 3
        self.active = True
        self.pulse = 0
        
    def update(self):
        self.pulse = (self.pulse + 2) % 360
        
    def draw(self):
        if not self.active:
            return
            
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        
        # Pulsing effect
        pulse_size = 1 + 0.2 * math.sin(math.radians(self.pulse))
        
        glColor3f(0.0, 0.8, 0.0)
        glutSolidCylinder(self.radius * pulse_size, 0.2, 16, 1)
        
        # Beacon light
        glColor3f(0.0, 1.0, 0.0)
        glTranslatef(0, 0.5, 0)
        glutSolidCylinder(0.5, 2, 8, 1)
        
        glPopMatrix()

class Particle:
    def __init__(self, x, y, z, color, velocity, lifetime):
        self.x = x
        self.y = y
        self.z = z
        self.color = color
        self.vx, self.vy, self.vz = velocity
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.z += self.vz
        self.vy -= 0.01  # Gravity
        self.lifetime -= 1
        return self.lifetime > 0
        
    def draw(self):
        alpha = self.lifetime / self.max_lifetime
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        glColor4f(*self.color, alpha)
        glutSolidSphere(0.1, 6, 6)
        glPopMatrix()

class Game:
    def __init__(self):
        # Set up display
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.OPENGL | pygame.DOUBLEBUF)
        pygame.display.set_caption("PyGame 3D Shooter")
        
        # Set up OpenGL
        self.setup_opengl()
        
        # Initialize game objects
        self.player = Player()
        self.enemies = []
        self.bullets = []
        self.ammo_boxes = []
        self.obstacles = []
        self.escape_point = None
        self.particles = []
        
        # Game state
        self.level = 1
        self.game_state = "playing"  # "playing", "level_complete", "game_over"
        self.score = 0
        self.message = ""
        self.message_timer = 0
        
        # Generate initial level
        self.generate_level()
        
        # Load fonts
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)
        
        # Sound effects (simulated)
        self.sound_enabled = True
        
        # Crosshair
        self.crosshair_size = 20
        self.target_enemy = None
        
    def setup_opengl(self):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)
        
        # Set up lighting
        glLightfv(GL_LIGHT0, GL_POSITION, [10, 10, 10, 1])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1])
        
        # Set up projection
        glMatrixMode(GL_PROJECTION)
        gluPerspective(60, SCREEN_WIDTH / SCREEN_HEIGHT, 0.1, 100)
        glMatrixMode(GL_MODELVIEW)
        
    def generate_level(self):
        # Clear existing objects
        self.enemies.clear()
        self.ammo_boxes.clear()
        self.obstacles.clear()
        self.bullets.clear()
        self.particles.clear()
        
        # Reset player position
        self.player.x = 0
        self.player.z = 0
        self.player.health = 100
        self.player.ammo = 12
        self.player.alive = True
        
        # Generate terrain obstacles
        for _ in range(15):
            x = random.uniform(-20, 20)
            z = random.uniform(-20, 20)
            # Avoid spawning too close to player
            if abs(x) < 5 and abs(z) < 5:
                x += 10 * (1 if x >= 0 else -1)
                z += 10 * (1 if z >= 0 else -1)
                
            width = random.uniform(1, 3)
            height = random.uniform(1, 4)
            depth = random.uniform(1, 3)
            self.obstacles.append(Obstacle(x, z, width, height, depth))
            
        # Generate enemies
        num_enemies = 3 + self.level
        for _ in range(num_enemies):
            x = random.uniform(-18, 18)
            z = random.uniform(-18, 18)
            # Avoid spawning too close to player
            if abs(x) < 8 and abs(z) < 8:
                x += 12 * (1 if x >= 0 else -1)
                z += 12 * (1 if z >= 0 else -1)
                
            enemy_type = "sniper" if random.random() > 0.7 else "soldier"
            self.enemies.append(Enemy(x, z, enemy_type))
            
        # Generate ammo boxes
        num_ammo_boxes = 4 + self.level
        for _ in range(num_ammo_boxes):
            x = random.uniform(-18, 18)
            z = random.uniform(-18, 18)
            # Avoid spawning too close to player
            if abs(x) < 5 and abs(z) < 5:
                x += 8 * (1 if x >= 0 else -1)
                z += 8 * (1 if z >= 0 else -1)
            self.ammo_boxes.append(AmmoBox(x, z))
            
        # Generate escape point
        x = random.uniform(-15, 15)
        z = random.uniform(-15, 15)
        # Ensure escape point is not too close to player
        while abs(x) < 10 and abs(z) < 10:
            x = random.uniform(-15, 15)
            z = random.uniform(-15, 15)
        self.escape_point = EscapePoint(x, z)
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_r and self.game_state != "playing":
                    self.restart_game()
                elif event.key == pygame.K_n and self.game_state == "level_complete":
                    self.next_level()
                elif event.key == pygame.K_SPACE and self.game_state == "playing":
                    self.player_shoot()
                    
            elif event.type == pygame.MOUSEMOTION:
                # Update player angle based on mouse movement
                if self.game_state == "playing":
                    dx = event.rel[0]
                    self.player.angle += dx * 0.2
                    
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and self.game_state == "playing":  # Left click
                    self.player_shoot()
                    
        return True
        
    def update(self):
        if self.game_state != "playing":
            return
            
        # Update message timer
        if self.message_timer > 0:
            self.message_timer -= 1
            if self.message_timer == 0:
                self.message = ""
                
        # Update player
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.player.move_forward()
        if keys[pygame.K_s]:
            self.player.move_backward()
        if keys[pygame.K_a]:
            self.player.move_left()
        if keys[pygame.K_d]:
            self.player.move_right()
            
        # Check collisions with obstacles
        self.check_collisions()
        
        # Update enemies
        for enemy in self.enemies[:]:
            if enemy.alive:
                if enemy.update(self.player):
                    # Enemy is shooting
                    self.enemy_shoot(enemy)
                    
        # Update bullets
        for bullet in self.bullets[:]:
            if not bullet.update():
                self.bullets.remove(bullet)
            else:
                # Check bullet collisions
                self.check_bullet_collisions(bullet)
                
        # Update ammo boxes
        for ammo_box in self.ammo_boxes:
            ammo_box.update()
            
        # Update escape point
        if self.escape_point:
            self.escape_point.update()
            
        # Update particles
        for particle in self.particles[:]:
            if not particle.update():
                self.particles.remove(particle)
                
        # Check if player reached escape point
        if self.escape_point and self.escape_point.active:
            dx = self.player.x - self.escape_point.x
            dz = self.player.z - self.escape_point.z
            distance = math.sqrt(dx*dx + dz*dz)
            if distance < self.escape_point.radius:
                self.level_complete("escape")
                
        # Check if all enemies are defeated
        if all(not enemy.alive for enemy in self.enemies):
            self.level_complete("enemies")
            
        # Check if player is dead
        if self.player.health <= 0:
            self.player.alive = False
            self.game_state = "game_over"
            
    def check_collisions(self):
        # Check player collision with obstacles
        for obstacle in self.obstacles:
            dx = abs(self.player.x - obstacle.x)
            dz = abs(self.player.z - obstacle.z)
            if dx < (0.5 + obstacle.width/2) and dz < (0.5 + obstacle.depth/2):
                # Push player back
                if dx > dz:
                    self.player.x += 0.1 if self.player.x < obstacle.x else -0.1
                else:
                    self.player.z += 0.1 if self.player.z < obstacle.z else -0.1
                    
        # Check player collision with ammo boxes
        for ammo_box in self.ammo_boxes[:]:
            if not ammo_box.collected:
                dx = self.player.x - ammo_box.x
                dz = self.player.z - ammo_box.z
                distance = math.sqrt(dx*dx + dz*dz)
                if distance < 1.5:
                    ammo_box.collected = True
                    self.player.ammo += 8
                    self.show_message("Ammo collected! +8", 60)
                    self.ammo_boxes.remove(ammo_box)
                    
    def check_bullet_collisions(self, bullet):
        # Check bullet collision with obstacles
        for obstacle in self.obstacles:
            dx = abs(bullet.x - obstacle.x)
            dz = abs(bullet.z - obstacle.z)
            if dx < (0.1 + obstacle.width/2) and dz < (0.1 + obstacle.depth/2):
                if bullet in self.bullets:
                    self.bullets.remove(bullet)
                # Create impact particles
                for _ in range(5):
                    velocity = (
                        random.uniform(-0.05, 0.05),
                        random.uniform(0, 0.1),
                        random.uniform(-0.05, 0.05)
                    )
                    self.particles.append(Particle(
                        bullet.x, bullet.y, bullet.z,
                        (0.7, 0.7, 0.7), velocity, 30
                    ))
                return
                
        if bullet.is_player_bullet:
            # Check player bullet collision with enemies
            for enemy in self.enemies:
                if enemy.alive:
                    dx = bullet.x - enemy.x
                    dz = bullet.z - enemy.z
                    distance = math.sqrt(dx*dx + dz*dz)
                    if distance < 1.0:
                        enemy.health -= 50
                        if enemy.health <= 0:
                            enemy.alive = False
                            self.score += 100
                            # Create death particles
                            for _ in range(10):
                                velocity = (
                                    random.uniform(-0.1, 0.1),
                                    random.uniform(0, 0.2),
                                    random.uniform(-0.1, 0.1)
                                )
                                self.particles.append(Particle(
                                    enemy.x, enemy.y + enemy.height/2, enemy.z,
                                    enemy.color, velocity, 60
                                ))
                        if bullet in self.bullets:
                            self.bullets.remove(bullet)
                        return
        else:
            # Check enemy bullet collision with player
            dx = bullet.x - self.player.x
            dz = bullet.z - self.player.z
            distance = math.sqrt(dx*dx + dz*dz)
            if distance < 1.0:
                self.player.health -= 10
                if bullet in self.bullets:
                    self.bullets.remove(bullet)
                # Create hit particles
                for _ in range(5):
                    velocity = (
                        random.uniform(-0.05, 0.05),
                        random.uniform(0, 0.1),
                        random.uniform(-0.05, 0.05)
                    )
                    self.particles.append(Particle(
                        self.player.x, self.player.y + self.player.height, self.player.z,
                        (1.0, 0.0, 0.0), velocity, 30
                    ))
                    
    def player_shoot(self):
        if self.player.ammo > 0 and self.player.alive:
            self.player.ammo -= 1
            self.bullets.append(Bullet(
                self.player.x, self.player.z, self.player.angle, 0.3, True
            ))
            # Create muzzle flash particles
            for _ in range(5):
                velocity = (
                    math.sin(math.radians(self.player.angle)) * 0.1,
                    random.uniform(-0.05, 0.05),
                    math.cos(math.radians(self.player.angle)) * 0.1
                )
                self.particles.append(Particle(
                    self.player.x, self.player.y + self.player.height, self.player.z,
                    (1.0, 1.0, 0.0), velocity, 20
                ))
        elif self.player.ammo <= 0:
            self.show_message("No ammo!", 30)
            
    def enemy_shoot(self, enemy):
        self.bullets.append(Bullet(
            enemy.x, enemy.z, enemy.angle, 0.2, False
        ))
        
    def level_complete(self, reason):
        self.game_state = "level_complete"
        if reason == "enemies":
            self.show_message(f"Level {self.level} Complete! All enemies eliminated.", 180)
        else:
            self.show_message(f"Level {self.level} Complete! Reached escape point.", 180)
            
    def next_level(self):
        self.level += 1
        self.game_state = "playing"
        self.generate_level()
        
    def restart_game(self):
        self.level = 1
        self.score = 0
        self.game_state = "playing"
        self.generate_level()
        
    def show_message(self, message, duration):
        self.message = message
        self.message_timer = duration
        
    def draw_3d_scene(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # Set up camera based on player position and angle
        cam_x = self.player.x - math.sin(math.radians(self.player.angle)) * 2
        cam_z = self.player.z - math.cos(math.radians(self.player.angle)) * 2
        cam_y = self.player.y + 1
        
        gluLookAt(
            cam_x, cam_y, cam_z,  # Camera position
            self.player.x, self.player.y + 1, self.player.z,  # Look at point
            0, 1, 0  # Up vector
        )
        
        # Draw ground
        glColor3f(0.3, 0.6, 0.3)
        glBegin(GL_QUADS)
        glVertex3f(-30, 0, -30)
        glVertex3f(-30, 0, 30)
        glVertex3f(30, 0, 30)
        glVertex3f(30, 0, -30)
        glEnd()
        
        # Draw grid on ground
        glColor3f(0.4, 0.7, 0.4)
        glBegin(GL_LINES)
        for i in range(-30, 31, 5):
            glVertex3f(i, 0.01, -30)
            glVertex3f(i, 0.01, 30)
            glVertex3f(-30, 0.01, i)
            glVertex3f(30, 0.01, i)
        glEnd()
        
        # Draw obstacles
        for obstacle in self.obstacles:
            obstacle.draw()
            
        # Draw player
        self.player.draw()
        
        # Draw enemies
        for enemy in self.enemies:
            enemy.draw()
            
        # Draw bullets
        for bullet in self.bullets:
            bullet.draw()
            
        # Draw ammo boxes
        for ammo_box in self.ammo_boxes:
            ammo_box.draw()
            
        # Draw escape point
        if self.escape_point:
            self.escape_point.draw()
            
        # Draw particles
        glDisable(GL_LIGHTING)
        for particle in self.particles:
            particle.draw()
        glEnable(GL_LIGHTING)
        
    def draw_hud(self):
        # Switch to 2D rendering for HUD
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, SCREEN_WIDTH, SCREEN_HEIGHT, 0)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        
        # Draw HUD background
        pygame.draw.rect(self.screen, (0, 0, 0, 180), (10, 10, 300, 100), border_radius=10)
        
        # Draw health bar
        health_width = 200 * (self.player.health / 100)
        pygame.draw.rect(self.screen, RED, (120, 25, 200, 20), border_radius=5)
        pygame.draw.rect(self.screen, GREEN, (120, 25, health_width, 20), border_radius=5)
        health_text = self.small_font.render("HP:", True, WHITE)
        self.screen.blit(health_text, (80, 25))
        
        # Draw ammo
        ammo_text = self.small_font.render(f"Ammo: {self.player.ammo}", True, WHITE)
        self.screen.blit(ammo_text, (80, 55))
        
        # Draw level and score
        level_text = self.small_font.render(f"Level: {self.level}", True, WHITE)
        self.screen.blit(level_text, (80, 75))
        
        score_text = self.small_font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (200, 75))
        
        # Draw enemy count
        alive_enemies = sum(1 for enemy in self.enemies if enemy.alive)
        enemy_text = self.small_font.render(f"Enemies: {alive_enemies}", True, WHITE)
        self.screen.blit(enemy_text, (200, 55))
        
        # Draw crosshair
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        pygame.draw.line(self.screen, WHITE, (center_x - 15, center_y), (center_x + 15, center_y), 2)
        pygame.draw.line(self.screen, WHITE, (center_x, center_y - 15), (center_x, center_y + 15), 2)
        
        # Draw message
        if self.message:
            msg_surface = self.font.render(self.message, True, YELLOW)
            msg_rect = msg_surface.get_rect(center=(SCREEN_WIDTH//2, 50))
            self.screen.blit(msg_surface, msg_rect)
            
        # Draw game state messages
        if self.game_state == "level_complete":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            
            complete_text = self.font.render("Mission Accomplished!", True, GREEN)
            complete_rect = complete_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
            self.screen.blit(complete_text, complete_rect)
            
            if self.message:
                reason_text = self.small_font.render(self.message, True, WHITE)
                reason_rect = reason_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
                self.screen.blit(reason_text, reason_rect)
                
            next_text = self.small_font.render("Press N for Next Mission or R to Restart", True, YELLOW)
            next_rect = next_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
            self.screen.blit(next_text, next_rect)
            
        elif self.game_state == "game_over":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            
            game_over_text = self.font.render("Game Over", True, RED)
            game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
            self.screen.blit(game_over_text, game_over_rect)
            
            score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
            score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            self.screen.blit(score_text, score_rect)
            
            restart_text = self.small_font.render("Press R to Restart", True, YELLOW)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
            self.screen.blit(restart_text, restart_rect)
            
        # Restore 3D rendering
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        
    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            running = self.handle_events()
            self.update()
            self.draw_3d_scene()
            self.draw_hud()
            pygame.display.flip()
            clock.tick(FPS)
            
        pygame.quit()
        sys.exit()

# Initialize GLUT for shapes
from OpenGL.GLUT import *
glutInit()

if __name__ == "__main__":
    game = Game()
    game.run()