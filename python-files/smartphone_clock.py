import pygame
import datetime
import sys

# Initialize pygame
pygame.init()

# Screen setup
screen = pygame.display.set_mode((400, 300))
pygame.display.set_caption("Simple Clock")

# Font
font = pygame.font.SysFont('Arial', 48)

def main():
    print("Starting clock...")
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Get current time
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        
        # Clear screen
        screen.fill((0, 0, 0))
        
        # Draw time
        text = font.render(current_time, True, (255, 255, 255))
        screen.blit(text, (100, 100))
        
        # Update display
        pygame.display.flip()
        
        # Cap the frame rate
        pygame.time.Clock().tick(1)  # 1 FPS for clock
    
    pygame.quit()
    print("Clock closed.")

if __name__ == "__main__":
    main()