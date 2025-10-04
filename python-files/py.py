import pygame
import random
import math
import time

# Initialize pygame
pygame.init()

# Set up game window
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shape Collector")

# Define colors
WHITE = (255, 255, 255)
LIGHT_GRAY = (211, 211, 211)  # Light gray for eggs
YELLOW = (255, 255, 0)  # Yellow for squares
ORANGE_RED = (255, 69, 0)  # Orange-red for triangles
PURPLE = (128, 0, 128)  # Purple for pentagons and beta shapes
CYAN = (0, 255, 255)  # Cyan for hexagons
DARK_GREEN = (0, 128, 0) # Dark green for heptagons
BLUE = (0, 0, 255)  # Blue for legendary shapes
LIGHT_GRAY_SHADOW = (1, 1, 1)  # BLACK
GREEN = (0, 255, 0)
# Rainbow colors (flashing effect)
RAINBOW_COLORS = [
    (255, 0, 0),  # Red
    (255, 165, 0),  # Orange
    (255, 255, 0),  # Yellow
    (0, 255, 0),  # Green
    (0, 255, 255),  # Cyan
    (0, 0, 255),  # Blue
    (128, 0, 128),  # Purple
    (255, 105, 180),  # Pink
]

# Define font
font = pygame.font.SysFont('Arial', 30)

# Define the shape properties (rarity, xp, size)
shapes = {
    "egg": {"rarity": 1/3, "xp": 5, "color": LIGHT_GRAY, "size": 50},
    "square": {"rarity": 1/6, "xp": 20, "color": YELLOW, "size": 50},
    "triangle": {"rarity": 1/12, "xp": 100, "color": ORANGE_RED, "size": 50},
    "pentagon": {"rarity": 1/24, "xp": 500, "color": PURPLE, "size": 50},

    # Beta shapes (1.5x size and different rarities/XP)
    "beta_egg": {"rarity": 1/10, "xp": 25, "color": LIGHT_GRAY, "size": 75},  # 1.5x size
    "beta_square": {"rarity": 1/20, "xp": 100, "color": YELLOW, "size": 75},  # 1.5x size
    "beta_triangle": {"rarity": 1/40, "xp": 500, "color": ORANGE_RED, "size": 75},  # 1.5x size
    "beta_pentagon": {"rarity": 1/80, "xp": 2500, "color": PURPLE, "size": 75},  # 1.5x size
    
    # Hexagons
    "hexagon": {"rarity": 1/48, "xp": 2500, "color": CYAN, "size": 50},  # Normal hexagon
    "beta_hexagon": {"rarity": 1/160, "xp": 12500, "color": CYAN, "size": 75},  # Beta hexagon
    
    # Heptagons
    "heptagon": {"rarity": 1/96, "xp": 12500, "color": DARK_GREEN, "size": 50}, # Heptagon
    "beta_heptagon": {"rarity": 1/320, "xp": 62500, "color": DARK_GREEN, "size": 75}, # Beta heptagon

    # Alpha shapes (1.5x larger than beta)
    "alpha_egg": {"rarity": 1/33, "xp": 125, "color": LIGHT_GRAY, "size": 112},  # 1.5x beta size
    "alpha_square": {"rarity": 1/67, "xp": 500, "color": YELLOW, "size": 112},  # 1.5x beta size
    "alpha_triangle": {"rarity": 1/133, "xp": 2500, "color": ORANGE_RED, "size": 112},  # 1.5x beta size
    "alpha_pentagon": {"rarity": 1/267, "xp": 12500, "color": PURPLE, "size": 112},  # 1.5x beta size
    "alpha_hexagon": {"rarity": 1/533, "xp": 62500, "color": CYAN, "size": 112},  # 1.5x beta size
    "alpha_heptagon": {"rarity": 1/1065, "xp": 312500, "color": DARK_GREEN, "size": 112}, #1.5x beta size

    
}

# Add shiny variants (rarer and 500x more XP)
for shape in list(shapes.keys()):
    shiny_shape = "shiny_" + shape
    shapes[shiny_shape] = {
        "rarity": shapes[shape]["rarity"] / 1500,  # 1500 times rarer
        "xp": shapes[shape]["xp"] * 500,  # 500 times more XP
        "color": GREEN,  # Always green for shiny shapes
        "size": shapes[shape]["size"],  # Same size as the original shape
    }

# Add legendary variants (50 times rarer than shiny shapes, 100 times more XP)
for shape in list(shapes.keys()):
    legendary_shape = "legendary_" + shape
    if "shiny_" in shape:
        original_shape = shape.replace("shiny_", "")
    else:
        original_shape = shape
    
    shapes[legendary_shape] = {
        "rarity": shapes["shiny_" + original_shape]["rarity"] / 50,  # 50 times rarer than shiny
        "xp": shapes["shiny_" + original_shape]["xp"] * 100,  # 100 times more XP than shiny
        "color": BLUE,  # Always blue for legendary shapes
        "size": shapes[original_shape]["size"],  # Same size as the original shape
    }

# Add shadow variants (50 times rarer than legendary shapes, 45 times more XP)
for shape in list(shapes.keys()):
    shadow_shape = "shadow_" + shape
    if "legendary_" in shape:
        original_shape = shape.replace("legendary_", "")
    else:
        original_shape = shape
    
    shapes[shadow_shape] = {
        "rarity": shapes["legendary_" + original_shape]["rarity"] / 50,  # 50 times rarer than legendary
        "xp": shapes["legendary_" + original_shape]["xp"] * 45,  # 45 times more XP than legendary
        "color": LIGHT_GRAY_SHADOW,  # Always light gray (235, 235, 235) for shadow shapes
        "size": shapes[original_shape]["size"],  # Same size as the original shape
    }

# Add rainbow variants (5 times rarer than shadow shapes, flashing in rainbow colors)
for shape in list(shapes.keys()):
    rainbow_shape = "rainbow_" + shape
    if "shadow_" in shape:
        original_shape = shape.replace("shadow_", "")
    else:
        original_shape = shape
    
    shapes[rainbow_shape] = {
        "rarity": shapes["shadow_" + original_shape]["rarity"] / 5,  # 5 times rarer than shadow shapes
        "xp": shapes["shadow_" + original_shape]["xp"]/5,  # 5 times more xp than shadow shapes
        "color": (255, 0, 0),  # Default color will be red; will cycle through rainbow
        "size": shapes[original_shape]["size"],  # Same size as the original shape
    }

# Normalize rarity values so that they sum up to 1
total_rarity = sum(shape["rarity"] for shape in shapes.values())
for shape in shapes.values():
    shape["normalized_rarity"] = shape["rarity"] / total_rarity

# Shape class to represent the collectible objects
class Shape:
    def __init__(self, shape_type, x, y):
        self.shape_type = shape_type
        self.x = x
        self.y = y
        self.size = shapes[shape_type]["size"]
        self.rect = pygame.Rect(self.x - self.size // 2, self.y - self.size // 2, self.size, self.size)
        self.color = shapes[shape_type]["color"]
        self.xp = shapes[shape_type]["xp"]
        self.creation_time = time.time()  # Store the creation time for flashing colors

    def draw(self):
        current_time = time.time()
        if "rainbow" in self.shape_type:
            elapsed_time = current_time - self.creation_time
            color_index = int(elapsed_time) % len(RAINBOW_COLORS)
            self.color = RAINBOW_COLORS[color_index]  # Update the color to the next in the rainbow

        if self.shape_type == "egg" or "egg" in self.shape_type:
            pygame.draw.circle(screen, self.color, (self.x, self.y), self.size // 2)
        elif self.shape_type == "square" or "square" in self.shape_type:
            pygame.draw.rect(screen, self.color, self.rect)
        elif self.shape_type == "triangle" or "triangle" in self.shape_type:
            points = [(self.x, self.y - self.size // 2), 
                      (self.x + self.size // 2, self.y + self.size // 2),
                      (self.x - self.size // 2, self.y + self.size // 2)]
            pygame.draw.polygon(screen, self.color, points)
        elif self.shape_type == "pentagon" or "pentagon" in self.shape_type:
            points = [(self.x, self.y - self.size // 2), 
                      (self.x + self.size // 3, self.y - self.size // 4),
                      (self.x + self.size // 2, self.y + self.size // 4),
                      (self.x + self.size // 3, self.y + self.size // 2),
                      (self.x - self.size // 3, self.y + self.size // 2)]
            pygame.draw.polygon(screen, self.color, points)
        elif self.shape_type == "hexagon" or "hexagon" in self.shape_type:
            points = [(self.x + math.cos(math.radians(60 * i)) * self.size // 2, self.y + math.sin(math.radians(60 * i)) * self.size // 2) for i in range(6)]
            pygame.draw.polygon(screen, self.color, points)
        elif self.shape_type == "heptagon" or "heptagon" in self.shape_type:
            # Draw a heptagon (7 sides)
            points = [(self.x + math.cos(math.radians(360 * i / 7)) * self.size // 2, 
                       self.y + math.sin(math.radians(360 * i / 7)) * self.size // 2) for i in range(7)]
            pygame.draw.polygon(screen, self.color, points)

# Game class for the main game logic
class Game:
    def __init__(self):
        self.shapes = []
        self.score = 0
        self.shape_list_index = 0  # To track which shape is being shown in the shape list

    def generate_shape(self):
        shape_type = self.choose_shape_type()
        x = random.randint(50, WIDTH - 50)
        y = random.randint(50, HEIGHT - 50)
        return Shape(shape_type, x, y)

    def choose_shape_type(self):
        rand = random.random()
        cumulative_rarity = 0.0
        for shape_type, shape_data in shapes.items():
            cumulative_rarity += shape_data["normalized_rarity"]
            if rand <= cumulative_rarity:
                return shape_type
        return "egg"  # Fallback

    def update(self):
        if random.random() < 0.15:
            if len(self.shapes) < 100:
                self.shapes.append(self.generate_shape())

    def collect_shape(self, mouse_pos):
        for shape in self.shapes[:]:
            if shape.rect.collidepoint(mouse_pos):
                self.score += shape.xp
                self.shapes.remove(shape)

    def draw(self):
        screen.fill(WHITE)
        for shape in self.shapes:
            shape.draw()
        
        # Display the score
        score_text = font.render(f"Score: {self.score}", True, (0, 0, 0))
        screen.blit(score_text, (10, 10))

    def show_shape_list(self):
        # Show current shape
        shape_types = list(shapes.keys())
        current_shape = shape_types[self.shape_list_index]
        current_shape_data = shapes[current_shape]
        
        shape_image = pygame.Surface((current_shape_data["size"], current_shape_data["size"]))
        shape_image.fill(current_shape_data["color"])
        screen.blit(shape_image, (WIDTH // 2 - current_shape_data["size"] // 2, HEIGHT // 2 - current_shape_data["size"] // 2))
        
        # Show shape name and XP
        shape_name_text = font.render(current_shape, True, (0, 0, 0))
        xp_text = font.render(f"XP: {current_shape_data['xp']}", True, (0, 0, 0))
        screen.blit(shape_name_text, (WIDTH // 2 - shape_name_text.get_width() // 2, HEIGHT // 2 + 100))
        screen.blit(xp_text, (WIDTH // 2 - xp_text.get_width() // 2, HEIGHT // 2 + 140))

# Start Menu class to handle main menu interactions
class StartMenu:
    def __init__(self):
        self.play_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 50, 200, 50)
        self.shape_list_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 10, 200, 50)

    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.play_button.collidepoint(event.pos):
                return "play"
            elif self.shape_list_button.collidepoint(event.pos):
                return "shape_list"
        return None

    def draw(self):
        pygame.draw.rect(screen, (0, 255, 0), self.play_button)
        pygame.draw.rect(screen, (0, 255, 255), self.shape_list_button)
        play_text = font.render("Play", True, (255, 255, 255))
        shape_list_text = font.render("Shape List(WIP)", True, (255, 255, 255))
        screen.blit(play_text, (WIDTH // 2 - play_text.get_width() // 2, HEIGHT // 2 - 40))
        screen.blit(shape_list_text, (WIDTH // 2 - shape_list_text.get_width() // 2, HEIGHT // 2 + 20))

def main():
    clock = pygame.time.Clock()
    start_menu = StartMenu()
    game = Game()
    menu_active = True
    game_active = False
    shape_list_active = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if menu_active:
                action = start_menu.handle_input(event)
                if action == "play":
                    menu_active = False
                    game_active = True
                elif action == "shape_list":
                    menu_active = False
                    shape_list_active = True
            elif game_active:
                game.update()
                game.collect_shape(event.pos) if event.type == pygame.MOUSEBUTTONDOWN else None
            elif shape_list_active:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:
                        game.shape_list_index += 1
                        if game.shape_list_index >= len(shapes):
                            game.shape_list_index = 0  # Loop back to the first shape

                # Show shape list
                game.show_shape_list()

            # Draw the appropriate screen
            start_menu.draw() if menu_active else game.draw()

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()