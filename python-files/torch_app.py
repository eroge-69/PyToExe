import tkinter as tk
from tkinter import Canvas
import math

class TorchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Torch Game")
        self.root.geometry("800x600")
        self.root.configure(bg='black')
        
        # Torch state
        self.torch_on = False
        self.torch_type = "flashlight"  # "flashlight" or "flaming"
        
        # Create canvas
        self.canvas = Canvas(root, width=800, height=600, bg='black', highlightthickness=0)
        self.canvas.pack(expand=True, fill='both')
        
        # Bind events
        self.canvas.bind("<Button-1>", self.toggle_torch)
        self.root.bind("<Key>", self.handle_keypress)
        
        # Draw initial torch (off state)
        self.draw_torch()
        
        # Add instructions
        self.draw_instructions()
    
    def draw_torch(self):
        # Clear canvas
        self.canvas.delete("torch", "light_beam", "flame")
        
        if self.torch_type == "flashlight":
            self.draw_flashlight()
        else:
            self.draw_flaming_torch()
    
    def draw_flashlight(self):
        """Draw the horizontal flashlight torch"""
        # Torch position and dimensions (horizontal orientation)
        torch_x, torch_y = 200, 300
        torch_width = 120  # Longer for horizontal
        torch_height = 60  # Shorter for horizontal
        
        # Draw torch body (black cylinder) - horizontal
        self.canvas.create_rectangle(
            torch_x, torch_y, 
            torch_x + torch_width, torch_y + torch_height,
            fill='black', outline='white', width=2,
            tags="torch"
        )
        
        # Draw torch head (circular) - at the right end
        head_radius = 35
        head_x = torch_x + torch_width + 10  # Position head at the right end
        head_y = torch_y + torch_height // 2  # Center vertically
        
        if self.torch_on:
            # Torch head when ON (yellow)
            self.canvas.create_oval(
                head_x - head_radius, head_y - head_radius,
                head_x + head_radius, head_y + head_radius,
                fill='yellow', outline='white', width=2,
                tags="torch"
            )
            
            # Draw light beam when torch is on
            self.draw_light_beam(head_x, head_y)
        else:
            # Torch head when OFF (dark gray)
            self.canvas.create_oval(
                head_x - head_radius, head_y - head_radius,
                head_x + head_radius, head_y + head_radius,
                fill='#333333', outline='white', width=2,
                tags="torch"
            )
        
        # Draw torch handle details - horizontal grip
        handle_x = torch_x + 20
        handle_y = torch_y + 10
        self.canvas.create_rectangle(
            handle_x, handle_y,
            handle_x + 15, handle_y + 40,
            fill='#444444', outline='white', width=1,
            tags="torch"
        )
    
    def draw_flaming_torch(self):
        """Draw the vertical flaming torch"""
        # Torch position and dimensions (vertical orientation)
        torch_x, torch_y = 350, 200
        torch_width = 40
        torch_height = 120
        
        # Draw torch handle (dark gray cylinder) - vertical
        self.canvas.create_rectangle(
            torch_x, torch_y, 
            torch_x + torch_width, torch_y + torch_height,
            fill='#444444', outline='white', width=2,
            tags="torch"
        )
        
        # Add highlight on the left side of handle
        highlight_width = 8
        self.canvas.create_rectangle(
            torch_x, torch_y,
            torch_x + highlight_width, torch_y + torch_height,
            fill='#666666', outline='', width=0,
            tags="torch"
        )
        
        # Draw flat top surface
        self.canvas.create_rectangle(
            torch_x, torch_y,
            torch_x + torch_width, torch_y + 5,
            fill='#333333', outline='white', width=1,
            tags="torch"
        )
        
        # Draw flame at the top
        flame_x = torch_x + torch_width // 2
        flame_y = torch_y
        
        if self.torch_on:
            # Draw main flame (orange outer layer)
            flame_points = [
                flame_x - 15, flame_y - 10,  # Top left
                flame_x + 15, flame_y - 10,  # Top right
                flame_x + 8, flame_y - 50,   # Right point
                flame_x, flame_y - 60,       # Top point
                flame_x - 8, flame_y - 50    # Left point
            ]
            self.canvas.create_polygon(
                flame_points,
                fill='orange', outline='white', width=1,
                tags="flame"
            )
            
            # Draw inner flame (yellow hottest part)
            inner_flame_points = [
                flame_x - 8, flame_y - 15,   # Top left
                flame_x + 8, flame_y - 15,   # Top right
                flame_x + 4, flame_y - 40,   # Right point
                flame_x, flame_y - 45,       # Top point
                flame_x - 4, flame_y - 40    # Left point
            ]
            self.canvas.create_polygon(
                inner_flame_points,
                fill='yellow', outline='', width=0,
                tags="flame"
            )
            
            # Draw flickering embers
            ember_positions = [
                (flame_x - 5, flame_y - 25),
                (flame_x + 5, flame_y - 30),
                (flame_x - 3, flame_y - 35),
                (flame_x + 8, flame_y - 20)
            ]
            
            for ember_x, ember_y in ember_positions:
                self.canvas.create_oval(
                    ember_x - 2, ember_y - 2,
                    ember_x + 2, ember_y + 2,
                    fill='orange', outline='', width=0,
                    tags="flame"
                )
        else:
            # Draw extinguished flame (dark gray)
            flame_points = [
                flame_x - 15, flame_y - 10,
                flame_x + 15, flame_y - 10,
                flame_x + 8, flame_y - 30,
                flame_x, flame_y - 35,
                flame_x - 8, flame_y - 30
            ]
            self.canvas.create_polygon(
                flame_points,
                fill='#333333', outline='white', width=1,
                tags="flame"
            )
    
    def draw_light_beam(self, start_x, start_y):
        """Draw a yellow light beam emanating from the torch head"""
        # Light beam parameters
        beam_length = 400
        beam_start_width = 20
        beam_end_width = 200
        
        # Create light beam as a polygon - pointing to the right (forward)
        points = [
            start_x + beam_start_width, start_y - beam_start_width,  # Top start
            start_x + beam_start_width, start_y + beam_start_width,  # Bottom start
            start_x + beam_length, start_y + beam_end_width,  # Bottom end
            start_x + beam_length, start_y - beam_end_width   # Top end
        ]
        
        # Draw the light beam
        self.canvas.create_polygon(
            points,
            fill='yellow', outline='orange', width=2,
            tags="light_beam"
        )
        
        # Add some glow effect with additional beams
        for i in range(3):
            glow_width = beam_start_width + (i * 5)
            glow_end_width = beam_end_width + (i * 10)
            glow_points = [
                start_x + glow_width, start_y - glow_width,
                start_x + glow_width, start_y + glow_width,
                start_x + beam_length, start_y + glow_end_width,
                start_x + beam_length, start_y - glow_end_width
            ]
            self.canvas.create_polygon(
                glow_points,
                fill='', outline='yellow', width=1,
                tags="light_beam"
            )
    
    def draw_instructions(self):
        """Draw instructions on the canvas"""
        # Clear previous instructions
        self.canvas.delete("instructions")
        
        if self.torch_type == "flashlight":
            self.canvas.create_text(
                400, 500,
                text="Click the flashlight to turn it ON/OFF",
                fill='white',
                font=('Arial', 16, 'bold'),
                tags="instructions"
            )
            
            self.canvas.create_text(
                400, 530,
                text="The light beam appears when the flashlight is ON",
                fill='white',
                font=('Arial', 12),
                tags="instructions"
            )
        else:
            self.canvas.create_text(
                400, 500,
                text="Click the flaming torch to light/extinguish it",
                fill='white',
                font=('Arial', 16, 'bold'),
                tags="instructions"
            )
            
            self.canvas.create_text(
                400, 530,
                text="The flame appears when the torch is lit",
                fill='white',
                font=('Arial', 12),
                tags="instructions"
            )
        
        # Common instructions
        self.canvas.create_text(
            400, 560,
            text="Press SHIFT + C to switch between flashlight and flaming torch",
            fill='yellow',
            font=('Arial', 12, 'bold'),
            tags="instructions"
        )
    
    def handle_keypress(self, event):
        """Handle keyboard input for switching torch types"""
        if event.state & 0x1:  # Shift key is pressed
            if event.keysym.lower() == 'c':
                # Switch torch type
                self.torch_type = "flaming" if self.torch_type == "flashlight" else "flashlight"
                self.torch_on = False  # Reset to off state when switching
                self.draw_torch()
                self.draw_instructions()
    
    def toggle_torch(self, event):
        """Toggle torch on/off when clicked"""
        if self.torch_type == "flashlight":
            # Check if click is near the flashlight (horizontal orientation)
            torch_x, torch_y = 200, 300
            torch_width = 120
            torch_height = 60
            head_radius = 35
            head_x = torch_x + torch_width + 10
            head_y = torch_y + torch_height // 2
            
            # Check if click is in torch body or head area
            if (torch_x <= event.x <= torch_x + torch_width and 
                torch_y <= event.y <= torch_y + torch_height) or \
               (abs(event.x - head_x) <= head_radius and 
                abs(event.y - head_y) <= head_radius):
                
                self.torch_on = not self.torch_on
                self.draw_torch()
                
                # Add a small visual feedback
                if self.torch_on:
                    self.root.configure(bg='#111111')  # Slightly lighter background when torch is on
                else:
                    self.root.configure(bg='black')    # Dark background when torch is off
        else:
            # Check if click is near the flaming torch (vertical orientation)
            torch_x, torch_y = 350, 200
            torch_width = 40
            torch_height = 120
            flame_height = 60
            
            # Check if click is in torch handle or flame area
            if (torch_x <= event.x <= torch_x + torch_width and 
                torch_y <= event.y <= torch_y + torch_height) or \
               (torch_x - 20 <= event.x <= torch_x + torch_width + 20 and 
                torch_y - flame_height <= event.y <= torch_y):
                
                self.torch_on = not self.torch_on
                self.draw_torch()
                
                # Add a small visual feedback
                if self.torch_on:
                    self.root.configure(bg='#111111')  # Slightly lighter background when torch is on
                else:
                    self.root.configure(bg='black')    # Dark background when torch is off

def main():
    root = tk.Tk()
    app = TorchApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 