import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import math
import random

# Game constants
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FOV = 70
RENDER_DISTANCE = 10
BLOCK_SIZE = 1.0

# Block types
BLOCK_AIR = 0
BLOCK_GRASS = 1
BLOCK_DIRT = 2
BLOCK_STONE = 3
BLOCK_WOOD = 4
BLOCK_LEAVES = 5
BLOCK_SAND = 6
BLOCK_WATER = 7

# Block colors (RGB)
BLOCK_COLORS = {
    BLOCK_GRASS: [(0.2, 0.8, 0.2), (0.6, 0.4, 0.2), (0.6, 0.4, 0.2), (0.6, 0.4, 0.2), (0.6, 0.4, 0.2), (0.2, 0.8, 0.2)],  # Top is green, sides are brown
    BLOCK_DIRT: [(0.6, 0.4, 0.2)] * 6,
    BLOCK_STONE: [(0.5, 0.5, 0.5)] * 6,
    BLOCK_WOOD: [(0.4, 0.25, 0.1), (0.4, 0.25, 0.1), (0.3, 0.2, 0.1), (0.3, 0.2, 0.1), (0.3, 0.2, 0.1), (0.3, 0.2, 0.1)],
    BLOCK_LEAVES: [(0.1, 0.6, 0.1)] * 6,
    BLOCK_SAND: [(0.9, 0.85, 0.6)] * 6,
    BLOCK_WATER: [(0.2, 0.4, 0.8, 0.6)] * 6,
}

class Camera:
    def __init__(self, position, yaw=-90, pitch=0):
        self.position = np.array(position, dtype=float)
        self.yaw = yaw
        self.pitch = pitch
        self.speed = 5.0
        self.sensitivity = 0.1
        self.update_vectors()
    
    def update_vectors(self):
        # Calculate direction vectors
        yaw_rad = math.radians(self.yaw)
        pitch_rad = math.radians(self.pitch)
        
        self.front = np.array([
            math.cos(yaw_rad) * math.cos(pitch_rad),
            math.sin(pitch_rad),
            math.sin(yaw_rad) * math.cos(pitch_rad)
        ])
        self.front = self.front / np.linalg.norm(self.front)
        
        self.right = np.cross(self.front, np.array([0, 1, 0]))
        self.right = self.right / np.linalg.norm(self.right)
        
        self.up = np.cross(self.right, self.front)
    
    def process_mouse(self, xoffset, yoffset):
        xoffset *= self.sensitivity
        yoffset *= self.sensitivity
        
        self.yaw += xoffset
        self.pitch += yoffset
        
        # Constrain pitch
        if self.pitch > 89.0:
            self.pitch = 89.0
        if self.pitch < -89.0:
            self.pitch = -89.0
        
        self.update_vectors()
    
    def get_view_matrix(self):
        glLoadIdentity()
        center = self.position + self.front
        gluLookAt(
            self.position[0], self.position[1], self.position[2],
            center[0], center[1], center[2],
            self.up[0], self.up[1], self.up[2]
        )

class World:
    def __init__(self, size=32):
        self.size = size
        self.blocks = {}
        self.generate_terrain()
    
    def generate_terrain(self):
        """Generate a simple terrain with hills"""
        for x in range(-self.size, self.size):
            for z in range(-self.size, self.size):
                # Simple height map using sine waves
                height = int(5 + 3 * math.sin(x * 0.1) * math.cos(z * 0.1))
                
                # Add some randomness
                height += random.randint(-1, 1)
                
                # Build terrain layers
                for y in range(height):
                    if y == height - 1:
                        self.set_block(x, y, z, BLOCK_GRASS)
                    elif y >= height - 4:
                        self.set_block(x, y, z, BLOCK_DIRT)
                    else:
                        self.set_block(x, y, z, BLOCK_STONE)
                
                # Add some trees
                if random.random() < 0.02 and height > 3:
                    self.generate_tree(x, height, z)
    
    def generate_tree(self, x, y, z):
        """Generate a simple tree"""
        # Trunk
        for i in range(4):
            self.set_block(x, y + i, z, BLOCK_WOOD)
        
        # Leaves
        for dx in range(-2, 3):
            for dz in range(-2, 3):
                for dy in range(3, 6):
                    if random.random() < 0.7:
                        self.set_block(x + dx, y + dy, z + dz, BLOCK_LEAVES)
    
    def set_block(self, x, y, z, block_type):
        if block_type == BLOCK_AIR:
            if (x, y, z) in self.blocks:
                del self.blocks[(x, y, z)]
        else:
            self.blocks[(x, y, z)] = block_type
    
    def get_block(self, x, y, z):
        return self.blocks.get((int(x), int(y), int(z)), BLOCK_AIR)
    
    def is_block_visible(self, x, y, z):
        """Check if any face of the block is visible"""
        if self.get_block(x, y, z) == BLOCK_AIR:
            return False
        
        # Check all 6 adjacent blocks
        adjacent = [
            (x, y+1, z), (x, y-1, z),
            (x+1, y, z), (x-1, y, z),
            (x, y, z+1), (x, y, z-1)
        ]
        
        for ax, ay, az in adjacent:
            if self.get_block(ax, ay, az) == BLOCK_AIR:
                return True
        return False

def draw_cube(x, y, z, block_type):
    """Draw a textured cube at the given position"""
    colors = BLOCK_COLORS.get(block_type, [(1, 1, 1)] * 6)
    
    vertices = [
        [x-0.5, y-0.5, z-0.5], [x+0.5, y-0.5, z-0.5],
        [x+0.5, y+0.5, z-0.5], [x-0.5, y+0.5, z-0.5],
        [x-0.5, y-0.5, z+0.5], [x+0.5, y-0.5, z+0.5],
        [x+0.5, y+0.5, z+0.5], [x-0.5, y+0.5, z+0.5]
    ]
    
    faces = [
        [0, 1, 2, 3],  # Front
        [4, 5, 6, 7],  # Back
        [0, 1, 5, 4],  # Bottom
        [2, 3, 7, 6],  # Top
        [0, 3, 7, 4],  # Left
        [1, 2, 6, 5]   # Right
    ]
    
    glBegin(GL_QUADS)
    for i, face in enumerate(faces):
        color = colors[i] if i < len(colors) else colors[0]
        if len(color) == 4:  # Has alpha
            glColor4f(*color)
        else:
            glColor3f(*color)
        
        for vertex in face:
            glVertex3fv(vertices[vertex])
    glEnd()
    
    # Draw edges for better visibility
    glColor3f(0, 0, 0)
    glLineWidth(1)
    glBegin(GL_LINES)
    edges = [
        [0, 1], [1, 2], [2, 3], [3, 0],
        [4, 5], [5, 6], [6, 7], [7, 4],
        [0, 4], [1, 5], [2, 6], [3, 7]
    ]
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()

def draw_crosshair():
    """Draw a simple crosshair in the center of the screen"""
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, WINDOW_WIDTH, WINDOW_HEIGHT, 0, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glDisable(GL_DEPTH_TEST)
    glColor3f(1, 1, 1)
    glLineWidth(2)
    
    cx, cy = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2
    size = 10
    
    glBegin(GL_LINES)
    glVertex2f(cx - size, cy)
    glVertex2f(cx + size, cy)
    glVertex2f(cx, cy - size)
    glVertex2f(cx, cy + size)
    glEnd()
    
    glEnable(GL_DEPTH_TEST)
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def ray_cast(camera, world, max_distance=10):
    """Cast a ray from camera to find the block being looked at"""
    direction = camera.front
    step = 0.1
    
    for i in range(int(max_distance / step)):
        pos = camera.position + direction * (i * step)
        x, y, z = int(pos[0]), int(pos[1]), int(pos[2])
        
        if world.get_block(x, y, z) != BLOCK_AIR:
            return (x, y, z)
    
    return None

def get_placement_position(camera, world, max_distance=10):
    """Get the position where a new block should be placed"""
    direction = camera.front
    step = 0.1
    last_pos = None
    
    for i in range(int(max_distance / step)):
        pos = camera.position + direction * (i * step)
        x, y, z = int(pos[0]), int(pos[1]), int(pos[2])
        
        if world.get_block(x, y, z) != BLOCK_AIR:
            return last_pos
        
        last_pos = (x, y, z)
    
    return None

def check_collision(position, world):
    """Check if position collides with any block"""
    x, y, z = int(position[0]), int(position[1]), int(position[2])
    
    # Check the block at player position and below
    for dy in [0, -1]:
        if world.get_block(x, y + dy, z) != BLOCK_AIR:
            return True
    
    return False

def main():
    # Initialize Pygame
    pygame.init()
    
    # Set up display with error handling
    try:
        display = (WINDOW_WIDTH, WINDOW_HEIGHT)
        pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
        pygame.display.set_caption("Minecraft 3D - Python Edition")
    except Exception as e:
        print(f"Error: Could not initialize display. This game requires a graphical environment.")
        print(f"Details: {e}")
        print("\nTo run this game:")
        print("1. Make sure you have a display/monitor connected")
        print("2. Run the game on a system with graphical capabilities")
        print("3. If on a remote server, use X11 forwarding or VNC")
        return
    
    # Hide and capture mouse
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)
    
    # Setup OpenGL
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    gluPerspective(FOV, (display[0] / display[1]), 0.1, 500.0)
    
    # Create world and camera
    world = World(size=20)
    camera = Camera([0, 10, 0])
    
    clock = pygame.time.Clock()
    
    # Game state
    selected_block = BLOCK_GRASS
    block_types = [BLOCK_GRASS, BLOCK_DIRT, BLOCK_STONE, BLOCK_WOOD, BLOCK_LEAVES, BLOCK_SAND]
    
    print("=== MINECRAFT 3D GAME ===")
    print("Controls:")
    print("  WASD - Move")
    print("  SPACE - Jump/Fly up")
    print("  SHIFT - Fly down")
    print("  Mouse - Look around")
    print("  Left Click - Break block")
    print("  Right Click - Place block")
    print("  1-6 - Select block type")
    print("  ESC - Exit")
    print("\nGenerating world...")
    
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                
                # Block selection
                if event.key == pygame.K_1:
                    selected_block = BLOCK_GRASS
                    print("Selected: Grass")
                elif event.key == pygame.K_2:
                    selected_block = BLOCK_DIRT
                    print("Selected: Dirt")
                elif event.key == pygame.K_3:
                    selected_block = BLOCK_STONE
                    print("Selected: Stone")
                elif event.key == pygame.K_4:
                    selected_block = BLOCK_WOOD
                    print("Selected: Wood")
                elif event.key == pygame.K_5:
                    selected_block = BLOCK_LEAVES
                    print("Selected: Leaves")
                elif event.key == pygame.K_6:
                    selected_block = BLOCK_SAND
                    print("Selected: Sand")
            
            if event.type == pygame.MOUSEMOTION:
                camera.process_mouse(event.rel[0], event.rel[1])
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click - break block
                    target = ray_cast(camera, world)
                    if target:
                        world.set_block(*target, BLOCK_AIR)
                        print(f"Broke block at {target}")
                
                elif event.button == 3:  # Right click - place block
                    target = get_placement_position(camera, world)
                    if target:
                        world.set_block(*target, selected_block)
                        print(f"Placed block at {target}")
        
        # Movement
        keys = pygame.key.get_pressed()
        velocity = camera.speed * dt
        
        new_position = camera.position.copy()
        
        if keys[pygame.K_w]:
            forward = camera.front.copy()
            forward[1] = 0  # Don't move up/down with forward
            forward = forward / np.linalg.norm(forward) if np.linalg.norm(forward) > 0 else forward
            new_position += forward * velocity
        if keys[pygame.K_s]:
            forward = camera.front.copy()
            forward[1] = 0
            forward = forward / np.linalg.norm(forward) if np.linalg.norm(forward) > 0 else forward
            new_position -= forward * velocity
        if keys[pygame.K_a]:
            new_position -= camera.right * velocity
        if keys[pygame.K_d]:
            new_position += camera.right * velocity
        if keys[pygame.K_SPACE]:
            new_position[1] += velocity
        if keys[pygame.K_LSHIFT]:
            new_position[1] -= velocity
        
        # Simple collision detection
        if not check_collision(new_position, world):
            camera.position = new_position
        
        # Rendering
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Sky color
        glClearColor(0.5, 0.7, 1.0, 1.0)
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        camera.get_view_matrix()
        
        # Render visible blocks
        rendered_blocks = 0
        for (x, y, z), block_type in world.blocks.items():
            # Simple frustum culling
            distance = np.linalg.norm(camera.position - np.array([x, y, z]))
            if distance < RENDER_DISTANCE * 2:
                if world.is_block_visible(x, y, z):
                    draw_cube(x, y, z, block_type)
                    rendered_blocks += 1
        
        # Draw crosshair
        draw_crosshair()
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    main()