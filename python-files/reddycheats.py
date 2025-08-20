import pygame
import sys
import numpy as np
import random
import win32gui
import win32con
import win32api
from pygame.locals import *

# Initialize pygame
pygame.init()

# Get screen size
screen_info = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = screen_info.current_w, screen_info.current_h

# Create a borderless window that stays on top
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.NOFRAME)
pygame.display.set_caption("Red Target Aim Overlay")
hwnd = pygame.display.get_wm_info()["window"]

# Set window to stay on top and transparent click-through
win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, 
                       win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | 
                       win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)
win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(0, 0, 0), 0, win32con.LWA_COLORKEY)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLUE = (0, 120, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GRAY = (100, 100, 100)
LIGHT_BLUE = (100, 150, 255)
DARK_GRAY = (50, 50, 50, 200)  # With alpha for transparency

class RedTargetAim:
    def __init__(self):
        # Targeting variables
        self.crosshair_size = 20
        self.target_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.right_click_down = False
        
        # Detection circle
        self.detection_radius = 150
        self.detection_circle_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        
        # Sensitivity settings
        self.sensitivity = 0.8  # 0.0 to 1.0 (0.0 = always miss, 1.0 = perfect accuracy)
        
        # Menu state
        self.menu_open = False
        
        # Font
        self.font = pygame.font.SysFont("Arial", 20)
        self.title_font = pygame.font.SysFont("Arial", 24, bold=True)
        
        # Slider for sensitivity
        self.slider_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 20, 200, 20)
        self.slider_knob = pygame.Rect(SCREEN_WIDTH // 2 - 100 + int(self.sensitivity * 200), 
                                      SCREEN_HEIGHT // 2 + 15, 10, 30)
        self.dragging_slider = False
        
        # Instructions
        self.instructions = [
            "RED TARGET AIM OVERLAY",
            "======================================",
            "• Hold RIGHT MOUSE to activate aim assist",
            "• Press F2 to open/close this menu",
            "• Adjust sensitivity with the slider",
            "• Red targets in the circle will be locked onto"
        ]
        
    def draw_detection_circle(self):
        # Draw the detection circle
        pygame.draw.circle(screen, LIGHT_BLUE, self.detection_circle_pos, self.detection_radius, 2)
        
        # Draw a cross in the center
        pygame.draw.line(screen, LIGHT_BLUE, 
                        (self.detection_circle_pos[0] - 10, self.detection_circle_pos[1]),
                        (self.detection_circle_pos[0] + 10, self.detection_circle_pos[1]), 2)
        pygame.draw.line(screen, LIGHT_BLUE, 
                        (self.detection_circle_pos[0], self.detection_circle_pos[1] - 10),
                        (self.detection_circle_pos[0], self.detection_circle_pos[1] + 10), 2)
        
    def draw_crosshair(self, pos):
        x, y = pos
        # Draw crosshair
        pygame.draw.line(screen, YELLOW, (x - self.crosshair_size, y), (x + self.crosshair_size, y), 2)
        pygame.draw.line(screen, YELLOW, (x, y - self.crosshair_size), (x, y + self.crosshair_size), 2)
        pygame.draw.circle(screen, YELLOW, (x, y), 8, 1)
        
    def find_red_target_in_circle(self):
        # Capture the screen
        screen_data = pygame.surfarray.array3d(pygame.display.get_surface())
        
        # Define lower and upper bounds for red in RGB
        lower_red = np.array([150, 0, 0])
        upper_red = np.array([255, 100, 100])
        
        # Create a mask for red pixels
        mask = np.all(np.logical_and(lower_red <= screen_data, screen_data <= upper_red), axis=2)
        
        # Get coordinates of red pixels
        red_y, red_x = np.where(mask)
        
        # Filter red pixels to only those within the detection circle
        circle_red_x = []
        circle_red_y = []
        
        for i in range(len(red_x)):
            dx = red_x[i] - self.detection_circle_pos[0]
            dy = red_y[i] - self.detection_circle_pos[1]
            if dx*dx + dy*dy <= self.detection_radius*self.detection_radius:
                circle_red_x.append(red_x[i])
                circle_red_y.append(red_y[i])
        
        if len(circle_red_x) > 0:
            # Calculate center of red pixels
            avg_x = int(np.mean(circle_red_x))
            avg_y = int(np.mean(circle_red_y))
            
            # Apply sensitivity (add some randomness if not 100% accurate)
            if self.sensitivity < 1.0:
                # Add random offset based on sensitivity
                max_offset = int(50 * (1 - self.sensitivity))
                avg_x += random.randint(-max_offset, max_offset)
                avg_y += random.randint(-max_offset, max_offset)
                
            return (avg_x, avg_y)
        
        return None
        
    def draw_menu(self):
        # Draw semi-transparent background
        menu_surface = pygame.Surface((400, 300), pygame.SRCALPHA)
        menu_surface.fill((50, 50, 50, 220))  # Semi-transparent dark gray
        
        # Draw border
        pygame.draw.rect(menu_surface, LIGHT_BLUE, (0, 0, 400, 300), 2)
        
        # Draw title
        title = self.title_font.render("AIM ASSIST SETTINGS", True, YELLOW)
        menu_surface.blit(title, (400 // 2 - title.get_width() // 2, 20))
        
        # Draw sensitivity text
        sens_text = self.font.render(f"Sensitivity: {self.sensitivity:.2f}", True, WHITE)
        menu_surface.blit(sens_text, (400 // 2 - sens_text.get_width() // 2, 70))
        
        # Draw slider
        pygame.draw.rect(menu_surface, GRAY, (100, 120, 200, 20))
        pygame.draw.rect(menu_surface, GREEN, (100, 120, int(self.sensitivity * 200), 20))
        pygame.draw.rect(menu_surface, YELLOW, (100 + int(self.sensitivity * 200) - 5, 115, 10, 30))
        
        # Draw slider labels
        low_text = self.font.render("Low", True, WHITE)
        high_text = self.font.render("High", True, WHITE)
        menu_surface.blit(low_text, (90, 145))
        menu_surface.blit(high_text, (305, 145))
        
        # Draw instructions
        for i, line in enumerate(self.instructions):
            text = self.font.render(line, True, WHITE)
            menu_surface.blit(text, (20, 180 + i*25))
        
        # Draw close hint
        close_text = self.font.render("Press F2 to close", True, YELLOW)
        menu_surface.blit(close_text, (400 // 2 - close_text.get_width() // 2, 260))
        
        # Blit the menu surface to the screen
        screen.blit(menu_surface, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 150))
        
    def draw_status(self):
        # Draw status in corner
        status = "AIM ASSIST: ACTIVE" if self.right_click_down else "AIM ASSIST: INACTIVE"
        color = GREEN if self.right_click_down else YELLOW
        text = self.font.render(status, True, color)
        screen.blit(text, (20, 20))
        
        # Draw sensitivity info
        sens_text = self.font.render(f"Sens: {self.sensitivity:.2f}", True, WHITE)
        screen.blit(sens_text, (20, 50))
        
        # Draw menu hint if menu is closed
        if not self.menu_open:
            hint_text = self.font.render("Press F2 for settings", True, LIGHT_BLUE)
            screen.blit(hint_text, (SCREEN_WIDTH - hint_text.get_width() - 20, 20))
        
    def run(self):
        clock = pygame.time.Clock()
        
        # Make window click-through when not in menu
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, 
                               win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | 
                               win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)
        
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == KEYDOWN:
                    if event.key == K_F2:
                        self.menu_open = not self.menu_open
                        # Toggle click-through
                        if self.menu_open:
                            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, 
                                                   win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) & 
                                                   ~win32con.WS_EX_TRANSPARENT)
                        else:
                            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, 
                                                   win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | 
                                                   win32con.WS_EX_TRANSPARENT)
                    elif event.key == K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                
                if event.type == MOUSEBUTTONDOWN:
                    if event.button == 3:  # Right mouse button
                        self.right_click_down = True
                    elif event.button == 1 and self.menu_open:  # Left mouse button in menu
                        # Check if clicking on slider knob
                        if self.slider_knob.collidepoint(event.pos):
                            self.dragging_slider = True
                
                if event.type == MOUSEBUTTONUP:
                    if event.button == 3:  # Right mouse button
                        self.right_click_down = False
                    elif event.button == 1:  # Left mouse button
                        self.dragging_slider = False
            
            # Handle slider dragging
            if self.dragging_slider and self.menu_open:
                mouse_x, _ = pygame.mouse.get_pos()
                # Constrain to slider area
                mouse_x = max(self.slider_rect.left, min(mouse_x, self.slider_rect.right))
                self.sensitivity = (mouse_x - self.slider_rect.left) / self.slider_rect.width
                self.slider_knob.x = mouse_x - 5
            
            # Clear screen with transparent color
            screen.fill(BLACK)
            
            # Find and aim at red targets if right click is held down
            if self.right_click_down:
                target = self.find_red_target_in_circle()
                if target:
                    self.target_pos = target
            
            # Draw the crosshair at target position
            self.draw_crosshair(self.target_pos)
            
            # Draw detection circle
            self.draw_detection_circle()
            
            # Draw status
            self.draw_status()
            
            # Draw menu if open
            if self.menu_open:
                self.draw_menu()
            
            pygame.display.flip()
            clock.tick(60)

if __name__ == "__main__":
    try:
        aim_assistant = RedTargetAim()
        aim_assistant.run()
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")