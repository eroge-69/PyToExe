import asyncio
import platform
import pygame
import random
import numpy as np

# Screen dimensions
WIDTH = 1280
HEIGHT = 1024
FPS = 30

# Initialize Pygame
def setup():
    global screen, display_surface
    pygame.init()
    # Set full-screen mode
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
    pygame.display.set_caption("Sonar Waterfall Display")
    display_surface = pygame.Surface((WIDTH, HEIGHT))
    
    # Fill initial surface with black
    display_surface.fill((0, 0, 0))

def update_loop():
    global display_surface
    
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            if platform.system() != "Emscripten":
                pygame.quit()
                return
    
    # Create a new random grayscale line (1 pixel high)
    line = np.random.randint(0, 256, (WIDTH,), dtype=np.uint8)
    
    # Shift the existing surface down by 1 pixel
    display_surface.scroll(0, 1)
    
    # Draw the new line at the top
    for x in range(WIDTH):
        gray = line[x]
        display_surface.set_at((x, 0), (gray, gray, gray))
    
    # Update the screen
    screen.blit(display_surface, (0, 0))
    pygame.display.flip()

async def main():
    setup()
    while True:
        update_loop()
        await asyncio.sleep(1.0 / FPS)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())