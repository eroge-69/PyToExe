import pygame
import sys
import math
import os

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Aim Assist Controller")

# Colors
BACKGROUND = (25, 25, 35)
PANEL_BG = (40, 40, 50)
TEXT_COLOR = (220, 220, 220)
BUTTON_COLOR = (60, 60, 75)
BUTTON_HOVER = (80, 80, 95)
BUTTON_ACTIVE = (0, 150, 200)
BORDER_COLOR = (80, 80, 90)
HIGHLIGHT = (0, 180, 255)
SLIDER_BG = (50, 50, 60)
SLIDER_FG = (0, 150, 200)

# Fonts
title_font = pygame.font.SysFont("Arial", 28, bold=True)
button_font = pygame.font.SysFont("Arial", 20)
status_font = pygame.font.SysFont("Arial", 18)
footer_font = pygame.font.SysFont("Arial", 16)
small_font = pygame.font.SysFont("Arial", 14)

# Button class
class Button:
    def __init__(self, x, y, width, height, text, id_name):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.id = id_name
        self.active = False
        self.hover = False
        
    def draw(self, surface):
        color = BUTTON_ACTIVE if self.active else BUTTON_HOVER if self.hover else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        pygame.draw.rect(surface, BORDER_COLOR, self.rect, 2, border_radius=5)
        
        text_surf = button_font.render(self.text, True, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def check_hover(self, pos):
        self.hover = self.rect.collidepoint(pos)
        return self.hover
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hover:
                # For mode buttons, deactivate others in the same group
                if self.id in ["linear", "exponential"]:
                    for btn in buttons:
                        if btn.id in ["linear", "exponential"]:
                            btn.active = False
                    self.active = True
                elif self.id in ["horizontal", "vertical", "doublemvm"]:
                    for btn in buttons:
                        if btn.id in ["horizontal", "vertical", "doublemvm"]:
                            btn.active = False
                    self.active = True
                else:
                    self.active = not self.active
                return True
        return False

# Slider class
class Slider:
    def __init__(self, x, y, width, height, min_val, max_val, initial, label):
        self.rect = pygame.Rect(x, y, width, height)
        self.handle_rect = pygame.Rect(x, y, 20, height + 10)
        self.min = min_val
        self.max = max_val
        self.value = initial
        self.label = label
        self.dragging = False
        self.update_position()
        
    def update_position(self):
        normalized = (self.value - self.min) / (self.max - self.min)
        self.handle_rect.centerx = self.rect.x + normalized * self.rect.width
        
    def draw(self, surface):
        # Draw slider background
        pygame.draw.rect(surface, SLIDER_BG, self.rect, border_radius=3)
        
        # Draw filled portion
        fill_width = int((self.value - self.min) / (self.max - self.min) * self.rect.width)
        fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_width, self.rect.height)
        pygame.draw.rect(surface, SLIDER_FG, fill_rect, border_radius=3)
        
        # Draw handle
        pygame.draw.rect(surface, HIGHLIGHT, self.handle_rect, border_radius=3)
        pygame.draw.rect(surface, BORDER_COLOR, self.handle_rect, 2, border_radius=3)
        
        # Draw label and value
        label_text = small_font.render(self.label, True, TEXT_COLOR)
        surface.blit(label_text, (self.rect.x, self.rect.y - 20))
        
        value_text = small_font.render(f"{self.value:.2f}", True, TEXT_COLOR)
        surface.blit(value_text, (self.rect.x + self.rect.width + 10, self.rect.y))
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.handle_rect.collidepoint(event.pos):
                self.dragging = True
                
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
            
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            # Update value based on mouse position
            rel_x = max(self.rect.x, min(event.pos[0], self.rect.x + self.rect.width))
            normalized = (rel_x - self.rect.x) / self.rect.width
            self.value = self.min + normalized * (self.max - self.min)
            self.update_position()
            return True
            
        return False

# Create buttons
buttons = []

# First column - Response Curve
buttons.append(Button(80, 100, 200, 40, "Linear", "linear"))
buttons.append(Button(80, 160, 200, 40, "Exponential", "exponential"))

# Second column - Load Zone
buttons.append(Button(350, 100, 200, 40, "Horizontal", "horizontal"))
buttons.append(Button(350, 160, 200, 40, "Vertical", "vertical"))
buttons.append(Button(350, 220, 200, 40, "DoubleMVM", "doublemvm"))
buttons.append(Button(350, 280, 200, 40, "Noise Filter", "noise_filter"))

# Third column - Toggles
buttons.append(Button(650, 100, 180, 40, "Reverse Mode", "reverse_mode"))
buttons.append(Button(650, 160, 180, 40, "Engine", "engine"))
buttons.append(Button(650, 220, 180, 40, "Block Keys", "block_keys"))

# Set initial states
for button in buttons:
    if button.id == "linear":
        button.active = True
    if button.id == "horizontal":
        button.active = True

# Create sliders
sliders = []
sliders.append(Slider(80, 350, 200, 15, 0.1, 5.0, 2.0, "Sensitivity"))
sliders.append(Slider(80, 400, 200, 15, 0.0, 1.0, 0.3, "Smoothing"))
sliders.append(Slider(80, 450, 200, 15, 0.0, 1.0, 0.5, "Acceleration"))
sliders.append(Slider(350, 350, 200, 15, 0, 100, 30, "Deadzone %"))
sliders.append(Slider(350, 400, 200, 15, 0, 100, 15, "Response Curve"))
sliders.append(Slider(350, 450, 200, 15, 1, 100, 25, "Filter Strength"))

# Mouse simulation
class MouseSimulator:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.radius = 10
        self.color = HIGHLIGHT
        self.original_pos = (self.x, self.y)
        self.trail = []
        self.max_trail = 10
        
    def draw(self, surface):
        # Draw trail
        for i, pos in enumerate(self.trail):
            alpha = int(255 * (i / len(self.trail)))
            color = (self.color[0], self.color[1], self.color[2], alpha)
            pygame.draw.circle(surface, color, pos, 3)
        
        # Draw crosshair
        pygame.draw.circle(surface, self.color, (self.x, self.y), self.radius, 2)
        pygame.draw.line(surface, self.color, (self.x - 15, self.y), (self.x + 15, self.y), 2)
        pygame.draw.line(surface, self.color, (self.x, self.y - 15), (self.x, self.y + 15), 2)
        
    def reset(self):
        self.x, self.y = self.original_pos
        self.trail = []
        
    def update(self, dx, dy):
        # Get sensitivity value
        sensitivity = sliders[0].value
        
        # Apply response curve
        response_curve = sliders[4].value / 100
        dx = math.copysign(abs(dx) ** (1 + response_curve), dx)
        dy = math.copysign(abs(dy) ** (1 + response_curve), dy)
        
        # Apply acceleration
        acceleration = sliders[2].value
        dx *= (1 + acceleration * abs(dx) / 10)
        dy *= (1 + acceleration * abs(dy) / 10)
        
        # Apply smoothing
        smoothing = sliders[1].value
        dx = smoothing * dx + (1 - smoothing) * dx
        dy = smoothing * dy + (1 - smoothing) * dy
        
        # Apply deadzone
        deadzone = sliders[3].value / 100
        if abs(dx) < deadzone:
            dx = 0
        if abs(dy) < deadzone:
            dy = 0
            
        # Apply filter strength
        filter_strength = sliders[5].value / 100
        dx *= (1 - filter_strength)
        dy *= (1 - filter_strength)
        
        # Apply reverse mode if active
        for button in buttons:
            if button.id == "reverse_mode" and button.active:
                dx = -dx
                dy = -dy
                
        # Update position
        self.x = max(self.radius, min(WIDTH - self.radius, self.x + dx * sensitivity))
        self.y = max(self.radius, min(HEIGHT - self.radius, self.y + dy * sensitivity))
        
        # Update trail
        self.trail.append((self.x, self.y))
        if len(self.trail) > self.max_trail:
            self.trail.pop(0)

# Create mouse simulator
mouse_sim = MouseSimulator()

# Main loop
clock = pygame.time.Clock()
running = True

while running:
    mouse_pos = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        for button in buttons:
            button.handle_event(event)
            
        for slider in sliders:
            slider.handle_event(event)
            
        # Handle keyboard shortcuts
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                running = False
            elif event.key == pygame.K_r:
                mouse_sim.reset()
            elif event.key == pygame.K_F1:
                for button in buttons:
                    if button.id == "reverse_mode":
                        button.active = not button.active
            elif event.key == pygame.K_F9:
                for button in buttons:
                    if button.id == "block_keys":
                        button.active = not button.active
            elif event.key == pygame.K_F10:
                for button in buttons:
                    if button.id == "engine":
                        button.active = not button.active
    
    # Update button hover states
    for button in buttons:
        button.check_hover(mouse_pos)
        
    # Update mouse simulation with real mouse movement
    dx, dy = pygame.mouse.get_rel()
    mouse_sim.update(dx, dy)
    
    # Draw everything
    screen.fill(BACKGROUND)
    
    # Draw title
    title_text = title_font.render("Aim Assist Controller", True, HIGHLIGHT)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 20))
    
    # Draw section labels
    curve_text = button_font.render("Response Curve", True, HIGHLIGHT)
    screen.blit(curve_text, (80, 70))
    
    load_zone_text = button_font.render("Load Zone", True, HIGHLIGHT)
    screen.blit(load_zone_text, (350, 70))
    
    toggle_text = button_font.render("Toggle Settings", True, HIGHLIGHT)
    screen.blit(toggle_text, (650, 70))
    
    # Draw buttons
    for button in buttons:
        button.draw(screen)
    
    # Draw sliders
    for slider in sliders:
        slider.draw(screen)
    
    # Draw mouse simulator
    mouse_sim.draw(screen)
    
    # Draw status indicators
    pygame.draw.rect(screen, PANEL_BG, (650, 280, 180, 150), border_radius=10)
    
    status_title = status_font.render("Status", True, HIGHLIGHT)
    screen.blit(status_title, (650 + 90 - status_title.get_width() // 2, 290))
    
    # Display active modes
    active_modes = [button.text for button in buttons if button.active]
    if active_modes:
        mode_text = small_font.render("Active: " + ", ".join(active_modes), True, TEXT_COLOR)
    else:
        mode_text = small_font.render("No active modes", True, TEXT_COLOR)
    screen.blit(mode_text, (650 + 90 - mode_text.get_width() // 2, 320))
    
    # Draw sensitivity value
    sens_text = small_font.render(f"Sensitivity: {sliders[0].value:.2f}", True, TEXT_COLOR)
    screen.blit(sens_text, (650 + 90 - sens_text.get_width() // 2, 350))
    
    # Draw footer with button hints
    pygame.draw.line(screen, BORDER_COLOR, (0, HEIGHT-40), (WIDTH, HEIGHT-40), 2)
    
    footer_text = footer_font.render("[E] Exit | [R] Reset Mouse | [F1] Reverse Mode | [F9] Block Keys | [F10] Engine", 
                                   True, TEXT_COLOR)
    screen.blit(footer_text, (WIDTH // 2 - footer_text.get_width() // 2, HEIGHT - 30))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()