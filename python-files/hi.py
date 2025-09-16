import tkinter as tk
from pynput.mouse import Button, Controller
import keyboard

class OnScreenMouse:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Mouse Controller")
        
        # Make window always on top but not transparent
        self.root.attributes('-topmost', True)
        self.root.overrideredirect(False)
        
        # Create frame
        self.frame = tk.Frame(self.root, relief='raised', borderwidth=3)
        self.frame.pack(padx=5, pady=5)
        
        # Create title bar
        self.title_bar = tk.Frame(self.frame, bg='lightgray', relief='raised', bd=2)
        self.title_bar.pack(fill='x', padx=2, pady=2)
        
        tk.Label(self.title_bar, text="Virtual Mouse", bg='lightgray').pack(side='left', padx=5)
        
        # Create buttons
        self.left_button = tk.Button(self.frame, text="Left Click", width=10,
                                   command=self.left_click)
        self.left_button.pack(padx=5, pady=2)
        
        self.middle_button = tk.Button(self.frame, text="Middle Click", width=10,
                                    command=self.middle_click)
        self.middle_button.pack(padx=5, pady=2)
        
        self.right_button = tk.Button(self.frame, text="Right Click", width=10,
                                    command=self.right_click)
        self.right_button.pack(padx=5, pady=2)
        
        # Initialize mouse controller
        self.mouse = Controller()
        
        # Make window draggable
        self.title_bar.bind('<B1-Motion>', self.move_window)
        self.title_bar.bind('<Button-1>', self.get_pos)
        
        # Bind escape key to quit
        keyboard.on_press_key('esc', lambda _: self.root.destroy())
        
        # Set window size and position
        self.root.geometry('150x120+100+100')
        
    def get_pos(self, event):
        """Get the position of window for dragging"""
        self.x = event.x
        self.y = event.y
        
    def move_window(self, event):
        """Move the window when dragged"""
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")
        
    def left_click(self):
        """Simulate left mouse click"""
        self.mouse.click(Button.left)
        
    def middle_click(self):
        """Simulate middle mouse click"""
        self.mouse.click(Button.middle)
        
    def right_click(self):
        """Simulate right mouse click"""
        self.mouse.click(Button.right)

if __name__ == "__main__":
    app = OnScreenMouse()
    app.root.mainloop()