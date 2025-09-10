import pygame
import sys
import random
import os

# Initialize pygame
pygame.init()
pygame.mixer.init()  # For sound effects

# Game Constants
# Default screen size (will be adjusted based on device)
BASE_SCREEN_WIDTH = 400
BASE_SCREEN_HEIGHT = 600

# Get actual screen size for mobile responsiveness
info = pygame.display.Info()
SCREEN_WIDTH = min(BASE_SCREEN_WIDTH, info.current_w)
SCREEN_HEIGHT = min(BASE_SCREEN_HEIGHT, info.current_h)

# Scale factors based on screen size
SCALE_FACTOR_X = SCREEN_WIDTH / BASE_SCREEN_WIDTH
SCALE_FACTOR_Y = SCREEN_HEIGHT / BASE_SCREEN_HEIGHT

GRAVITY = 0.25
BIRD_JUMP = -5
PIPE_GAP = int(150 * SCALE_FACTOR_Y)  # Scale gap based on screen height
PIPE_FREQUENCY = 1500  # milliseconds
GROUND_HEIGHT = int(100 * SCALE_FACTOR_Y)  # Scale ground height
SCROLL_SPEED = 3
FPS = 60

# Mobile settings
IS_MOBILE = True  # Set to True to enable mobile controls
IS_ANDROID = False
try:
    # Check if running on Android
    import android
    IS_ANDROID = True
except ImportError:
    pass

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKY_BLUE = (135, 206, 235)

# Create the screen
# For mobile, use fullscreen or the best fit mode
if IS_MOBILE:
    if IS_ANDROID:
        # Full screen mode for Android
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        SCREEN_WIDTH = pygame.display.Info().current_w
        SCREEN_HEIGHT = pygame.display.Info().current_h
        
        # Update scale factors after getting actual screen size
        SCALE_FACTOR_X = SCREEN_WIDTH / BASE_SCREEN_WIDTH
        SCALE_FACTOR_Y = SCREEN_HEIGHT / BASE_SCREEN_HEIGHT
        
        # Try to set Android orientation to landscape
        try:
            android.init()
            android.map_key(android.KEYCODE_BACK, pygame.K_ESCAPE)
            android.accelerometer_enable(True)
        except:
            pass
    else:
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SCALED | pygame.RESIZABLE)
else:
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

pygame.display.set_caption('Flappy Bird')
clock = pygame.time.Clock()

# Create assets directory if it doesn't exist
assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')
os.makedirs(assets_dir, exist_ok=True)

# Create SVG files for textures
def create_svg_files():
    # Background SVG
    background_svg = '''
    <svg width="400" height="600" xmlns="http://www.w3.org/2000/svg">
        <!-- Sky -->
        <rect width="400" height="600" fill="#87CEEB"/>
        
        <!-- Sun -->
        <circle cx="350" cy="80" r="40" fill="#FFD700"/>
        
        <!-- Clouds -->
        <g fill="#FFFFFF">
            <ellipse cx="100" cy="120" rx="40" ry="20"/>
            <ellipse cx="130" cy="120" rx="40" ry="25"/>
            <ellipse cx="70" cy="120" rx="30" ry="18"/>
            
            <ellipse cx="250" cy="180" rx="50" ry="25"/>
            <ellipse cx="290" cy="180" rx="40" ry="20"/>
            <ellipse cx="220" cy="180" rx="35" ry="18"/>
        </g>
        
        <!-- Distant mountains -->
        <path d="M0,500 L80,420 L120,450 L200,350 L250,420 L300,380 L350,430 L400,400 L400,500 Z" fill="#6B8E23"/>
    </svg>
    '''
    
    # Ground SVG
    ground_svg = '''
    <svg width="400" height="100" xmlns="http://www.w3.org/2000/svg">
        <!-- Ground -->
        <rect width="400" height="100" fill="#8B4513"/>
        
        <!-- Grass top -->
        <rect width="400" height="20" fill="#7CFC00"/>
        
        <!-- Grass details -->
        <g fill="#006400">
            <rect x="10" y="0" width="2" height="10"/>
            <rect x="30" y="0" width="2" height="12"/>
            <rect x="50" y="0" width="2" height="8"/>
            <rect x="70" y="0" width="2" height="11"/>
            <rect x="90" y="0" width="2" height="9"/>
            <rect x="110" y="0" width="2" height="10"/>
            <rect x="130" y="0" width="2" height="12"/>
            <rect x="150" y="0" width="2" height="8"/>
            <rect x="170" y="0" width="2" height="11"/>
            <rect x="190" y="0" width="2" height="9"/>
            <rect x="210" y="0" width="2" height="10"/>
            <rect x="230" y="0" width="2" height="12"/>
            <rect x="250" y="0" width="2" height="8"/>
            <rect x="270" y="0" width="2" height="11"/>
            <rect x="290" y="0" width="2" height="9"/>
            <rect x="310" y="0" width="2" height="10"/>
            <rect x="330" y="0" width="2" height="12"/>
            <rect x="350" y="0" width="2" height="8"/>
            <rect x="370" y="0" width="2" height="11"/>
            <rect x="390" y="0" width="2" height="9"/>
        </g>
        
        <!-- Dirt details -->
        <g fill="#A0522D">
            <rect x="20" y="30" width="30" height="10"/>
            <rect x="100" y="40" width="40" height="15"/>
            <rect x="200" y="35" width="25" height="12"/>
            <rect x="300" y="45" width="35" height="10"/>
        </g>
    </svg>
    '''
    
    # Bird SVG
    bird_svg = '''
    <svg width="40" height="30" xmlns="http://www.w3.org/2000/svg">
        <!-- Body -->
        <ellipse cx="20" cy="15" rx="18" ry="12" fill="#FFD700"/>
        
        <!-- Wing -->
        <ellipse cx="12" cy="18" rx="10" ry="6" fill="#FFA500" transform="rotate(-15 12 18)"/>
        
        <!-- Eye -->
        <circle cx="28" cy="10" r="3" fill="white"/>
        <circle cx="29" cy="10" r="1.5" fill="black"/>
        
        <!-- Beak -->
        <path d="M32,15 L40,12 L32,18 Z" fill="#FF4500"/>
    </svg>
    '''
    
    # Pipe SVG
    pipe_svg = '''
    <svg width="60" height="500" xmlns="http://www.w3.org/2000/svg">
        <!-- Main pipe -->
        <rect width="60" height="500" fill="#32CD32"/>
        
        <!-- Pipe border -->
        <rect x="0" y="0" width="60" height="500" fill="none" stroke="#006400" stroke-width="4"/>
        
        <!-- Pipe highlight -->
        <rect x="10" y="0" width="10" height="500" fill="#90EE90" opacity="0.5"/>
        
        <!-- Pipe end cap -->
        <rect x="-10" y="0" width="80" height="30" fill="#32CD32" stroke="#006400" stroke-width="4"/>
    </svg>
    '''
    
    # Game Over SVG
    game_over_svg = '''
    <svg width="300" height="200" xmlns="http://www.w3.org/2000/svg">
        <!-- Background -->
        <rect width="300" height="200" rx="20" ry="20" fill="#4682B4" opacity="0.8"/>
        
        <!-- Text -->
        <text x="150" y="80" font-family="Arial" font-size="32" font-weight="bold" fill="white" text-anchor="middle">GAME OVER</text>
        <text x="150" y="130" font-family="Arial" font-size="20" fill="white" text-anchor="middle">Press SPACE to restart</text>
    </svg>
    '''
    
    # Save SVG files
    with open(os.path.join(assets_dir, 'background.svg'), 'w') as f:
        f.write(background_svg)
    
    with open(os.path.join(assets_dir, 'ground.svg'), 'w') as f:
        f.write(ground_svg)
    
    with open(os.path.join(assets_dir, 'bird.svg'), 'w') as f:
        f.write(bird_svg)
    
    with open(os.path.join(assets_dir, 'pipe.svg'), 'w') as f:
        f.write(pipe_svg)
    
    with open(os.path.join(assets_dir, 'game_over.svg'), 'w') as f:
        f.write(game_over_svg)

# Create SVG files
create_svg_files()

# Load images
def load_svg_as_surface(svg_path, width=None, height=None):
    # This is a workaround since we can't directly load SVG in Pygame
    # In a real implementation, you'd use a library like CairoSVG or convert SVGs to PNGs beforehand
    # For this example, we'll create simple surfaces with colors
    
    if 'background' in svg_path:
        surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        surface.fill(SKY_BLUE)
        # Add simple cloud shapes
        pygame.draw.ellipse(surface, WHITE, (100, 100, 80, 40))
        pygame.draw.ellipse(surface, WHITE, (250, 150, 100, 50))
        return surface
    
    elif 'ground' in svg_path:
        surface = pygame.Surface((SCREEN_WIDTH, GROUND_HEIGHT))
        surface.fill((139, 69, 19))  # Brown
        pygame.draw.rect(surface, (124, 252, 0), (0, 0, SCREEN_WIDTH, 20))  # Green top
        return surface
    
    elif 'bird' in svg_path:
        surface = pygame.Surface((40, 30), pygame.SRCALPHA)
        # Yellow body
        pygame.draw.ellipse(surface, (255, 215, 0), (2, 3, 36, 24))
        # Orange wing
        pygame.draw.ellipse(surface, (255, 165, 0), (2, 12, 20, 12))
        # Eye
        pygame.draw.circle(surface, WHITE, (28, 10), 3)
        pygame.draw.circle(surface, BLACK, (29, 10), 1.5)
        # Beak
        pygame.draw.polygon(surface, (255, 69, 0), [(32, 15), (40, 12), (32, 18)])
        return surface
    
    elif 'pipe' in svg_path:
        surface = pygame.Surface((60, 500), pygame.SRCALPHA)
        surface.fill((50, 205, 50))  # Green
        # Border
        pygame.draw.rect(surface, (0, 100, 0), (0, 0, 60, 500), 4)
        # Highlight
        pygame.draw.rect(surface, (144, 238, 144, 128), (10, 0, 10, 500))
        # End cap
        pygame.draw.rect(surface, (50, 205, 50), (-10, 0, 80, 30))
        pygame.draw.rect(surface, (0, 100, 0), (-10, 0, 80, 30), 4)
        return surface
    
    elif 'game_over' in svg_path:
        surface = pygame.Surface((300, 200), pygame.SRCALPHA)
        # Background
        pygame.draw.rect(surface, (70, 130, 180, 204), (0, 0, 300, 200), border_radius=20)
        # We can't easily render text here, so we'll do that in the main game loop
        return surface
    
    # Default fallback
    return pygame.Surface((100, 100))

# Load game assets
background_img = load_svg_as_surface(os.path.join(assets_dir, 'background.svg'))
ground_img = load_svg_as_surface(os.path.join(assets_dir, 'ground.svg'))
bird_img = load_svg_as_surface(os.path.join(assets_dir, 'bird.svg'))
pipe_img = load_svg_as_surface(os.path.join(assets_dir, 'pipe.svg'))
game_over_img = load_svg_as_surface(os.path.join(assets_dir, 'game_over.svg'))

# Bird class
class Bird:
    def __init__(self):
        self.x = 100
        self.y = SCREEN_HEIGHT // 2
        self.velocity = 0
        self.img = bird_img
        self.rect = self.img.get_rect(center=(self.x, self.y))
        self.rotation = 0
        self.animation_frames = [bird_img]  # In a full game, you'd have multiple frames
        self.current_frame = 0
        self.animation_speed = 0.1
        self.animation_counter = 0
    
    def update(self):
        # Apply gravity
        self.velocity += GRAVITY
        self.y += self.velocity
        
        # Rotate bird based on velocity
        self.rotation = -self.velocity * 3 if self.velocity < 8 else -90
        
        # Update rectangle position
        self.rect.centery = self.y
        
        # Animate bird
        self.animation_counter += self.animation_speed
        if self.animation_counter >= len(self.animation_frames):
            self.animation_counter = 0
        self.current_frame = int(self.animation_counter)
    
    def jump(self):
        self.velocity = BIRD_JUMP
    
    def draw(self, surface):
        # Get current animation frame
        current_img = self.animation_frames[self.current_frame]
        
        # Rotate image
        rotated_img = pygame.transform.rotate(current_img, self.rotation)
        rotated_rect = rotated_img.get_rect(center=self.rect.center)
        
        # Draw bird
        surface.blit(rotated_img, rotated_rect.topleft)

# Pipe class
class Pipe:
    def __init__(self, x):
        self.x = x
        self.height = random.randint(150, 350)
        self.top_pipe = pygame.transform.flip(pipe_img, False, True)
        self.bottom_pipe = pipe_img
        self.passed = False
        
        # Calculate pipe positions
        self.top_rect = self.top_pipe.get_rect(bottomleft=(self.x, self.height - PIPE_GAP // 2))
        self.bottom_rect = self.bottom_pipe.get_rect(topleft=(self.x, self.height + PIPE_GAP // 2))
    
    def update(self):
        self.x -= SCROLL_SPEED
        self.top_rect.x = self.x
        self.bottom_rect.x = self.x
    
    def draw(self, surface):
        surface.blit(self.top_pipe, self.top_rect)
        surface.blit(self.bottom_pipe, self.bottom_rect)
    
    def collide(self, bird_rect):
        return bird_rect.colliderect(self.top_rect) or bird_rect.colliderect(self.bottom_rect)

# Ground class
class Ground:
    def __init__(self):
        self.x = 0
        self.y = SCREEN_HEIGHT - GROUND_HEIGHT
        self.img = ground_img
    
    def update(self):
        self.x -= SCROLL_SPEED
        if self.x <= -SCREEN_WIDTH:
            self.x = 0
    
    def draw(self, surface):
        # Draw ground twice to create scrolling effect
        surface.blit(self.img, (self.x, self.y))
        surface.blit(self.img, (self.x + SCREEN_WIDTH, self.y))

# Game class
class Game:
    def __init__(self):
        self.bird = Bird()
        self.pipes = []
        self.ground = Ground()
        self.score = 0
        self.high_score = 0
        self.game_active = False
        self.last_pipe = pygame.time.get_ticks() - PIPE_FREQUENCY
        self.font = pygame.font.SysFont('Arial', 36)
    
    def reset(self):
        self.bird = Bird()
        self.pipes = []
        self.score = 0
        self.game_active = True
        self.last_pipe = pygame.time.get_ticks()
    
    def update(self):
        if self.game_active:
            # Update bird
            self.bird.update()
            
            # Check for ground collision
            if self.bird.rect.bottom >= SCREEN_HEIGHT - GROUND_HEIGHT or self.bird.rect.top <= 0:
                self.game_active = False
            
            # Update and check pipes
            current_time = pygame.time.get_ticks()
            if current_time - self.last_pipe > PIPE_FREQUENCY:
                self.pipes.append(Pipe(SCREEN_WIDTH))
                self.last_pipe = current_time
            
            for pipe in self.pipes:
                pipe.update()
                
                # Check for collision
                if pipe.collide(self.bird.rect):
                    self.game_active = False
                
                # Check if pipe is passed
                if not pipe.passed and pipe.x + 60 < self.bird.x:
                    pipe.passed = True
                    self.score += 1
            
            # Remove off-screen pipes
            self.pipes = [pipe for pipe in self.pipes if pipe.x > -100]
            
            # Update ground
            self.ground.update()
            
            # Update high score
            if self.score > self.high_score:
                self.high_score = self.score
    
    def draw(self, surface):
        # Draw background
        surface.blit(background_img, (0, 0))
        
        # Draw pipes
        for pipe in self.pipes:
            pipe.draw(surface)
        
        # Draw ground
        self.ground.draw(surface)
        
        # Draw bird
        self.bird.draw(surface)
        
        # Draw score
        score_text = self.font.render(f'Score: {self.score}', True, WHITE)
        surface.blit(score_text, (10, 10))
        
        # Draw high score
        high_score_text = self.font.render(f'High Score: {self.high_score}', True, WHITE)
        surface.blit(high_score_text, (10, 50))
        
        # Draw game over screen
        if not self.game_active:
            surface.blit(game_over_img, ((SCREEN_WIDTH - 300) // 2, (SCREEN_HEIGHT - 200) // 2))
            
            # Draw text on game over screen
            game_over_text = self.font.render('GAME OVER', True, WHITE)
            
            # Different restart text based on platform
            if IS_MOBILE:
                restart_text = pygame.font.SysFont('Arial', 24).render('Tap to restart', True, WHITE)
            else:
                restart_text = pygame.font.SysFont('Arial', 24).render('Press SPACE to restart', True, WHITE)
            
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
            
            surface.blit(game_over_text, text_rect)
            surface.blit(restart_text, restart_rect)

# Main game loop
def main():
    # Make global variables accessible
    global SCREEN_WIDTH, SCREEN_HEIGHT, SCALE_FACTOR_X, SCALE_FACTOR_Y, GROUND_HEIGHT
    
    game = Game()
    running = True
    
    # For mobile touch detection
    touch_start_pos = None
    
    while running:
        # Handle Android-specific events
        if IS_ANDROID:
            try:
                if android.check_pause():
                    android.wait_for_resume()
            except:
                pass
                
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Handle escape key (mapped from Android back button)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    if game.game_active:
                        game.bird.jump()
                    else:
                        game.reset()
            
            # Touch controls (for mobile)
            if IS_MOBILE:
                # Handle touch events
                if event.type == pygame.FINGERDOWN:
                    # Convert touch position to screen coordinates
                    x = event.x * SCREEN_WIDTH
                    y = event.y * SCREEN_HEIGHT
                    touch_start_pos = (x, y)
                    
                    # Jump on tap
                    if game.game_active:
                        game.bird.jump()
                    else:
                        # Check if tap is on restart area
                        restart_area = pygame.Rect(
                            (SCREEN_WIDTH - 300) // 2,
                            (SCREEN_HEIGHT - 200) // 2,
                            300, 200
                        )
                        if restart_area.collidepoint(x, y):
                            game.reset()
                
                # Mouse click as fallback for testing on desktop
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if game.game_active:
                        game.bird.jump()
                    else:
                        # Check if click is on restart area
                        restart_area = pygame.Rect(
                            (SCREEN_WIDTH - 300) // 2,
                            (SCREEN_HEIGHT - 200) // 2,
                            300, 200
                        )
                        if restart_area.collidepoint(event.pos):
                            game.reset()
                            
        # Handle accelerometer input for Android as alternative control
        if IS_ANDROID:
            try:
                # Get accelerometer data (x, y, z)
                accel_data = android.accelerometer_reading()
                # Use y-axis tilt (landscape mode) to control jump
                # Threshold for jump trigger
                if accel_data[1] > 5 and game.game_active:
                    game.bird.jump()
            except:
                pass
            
            # Handle window resize events
            if event.type == pygame.VIDEORESIZE:
                # Update screen dimensions
                SCREEN_WIDTH = event.w
                SCREEN_HEIGHT = event.h
                
                # Recalculate scale factors
                SCALE_FACTOR_X = SCREEN_WIDTH / BASE_SCREEN_WIDTH
                SCALE_FACTOR_Y = SCREEN_HEIGHT / BASE_SCREEN_HEIGHT
                
                # Update game elements that depend on screen size
                game.ground.y = SCREEN_HEIGHT - GROUND_HEIGHT
        
        # Update game state
        game.update()
        
        # Draw everything
        game.draw(screen)
        
        # Update display
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()