import tkinter as tk
from threading import Timer
import time

class StopwatchWidget:
    def __init__(self):
        # Initialize timer variables
        self.start_time = 0.0
        self.elapsed_time = 0.0
        self.running = False
        self.timer_thread = None
        
        # Create main window
        self.root = tk.Tk()
        self.setup_window()
        self.setup_display()
        self.setup_bindings()
        
        # Start the update loop
        self.update_display()
    
    def setup_window(self):
        """Configure the main window properties"""
        # Remove title bar and make window unresizable
        self.root.overrideredirect(True)
        self.root.resizable(False, False)
        
        # Set fixed window size (half of original 200x80)
        self.root.geometry("100x40")
        
        # Set always on top
        self.root.attributes("-topmost", True)
        
        # Set transparency (40% opacity)
        self.root.attributes("-alpha", 0.4)
        
        # Set background color to black
        self.root.configure(bg="black")
        
        # Center the window on screen
        self.center_window()
        
        # Make window draggable
        self.setup_dragging()
    
    def center_window(self):
        """Center the window on the screen"""
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        x = (screen_width - 100) // 2
        y = (screen_height - 40) // 2
        
        self.root.geometry(f"100x40+{x}+{y}")
    
    def setup_dragging(self):
        """Enable window dragging functionality"""
        self.drag_start_x = 0
        self.drag_start_y = 0
        
        def start_drag(event):
            self.drag_start_x = event.x
            self.drag_start_y = event.y
        
        def do_drag(event):
            x = self.root.winfo_x() + event.x - self.drag_start_x
            y = self.root.winfo_y() + event.y - self.drag_start_y
            self.root.geometry(f"+{x}+{y}")
        
        # Bind dragging to the entire window
        self.root.bind("<Button-1>", start_drag)
        self.root.bind("<B1-Motion>", do_drag)
    
    def setup_display(self):
        """Create the time display label"""
        self.time_label = tk.Label(
            self.root,
            text="00:00",
            font=("Courier", 12, "bold"),  # Smaller font for smaller window
            fg="white",  # White text color
            bg="black",  # Black background color
            anchor="center"
        )
        
        # Center the label in the window with 15% margins
        self.time_label.place(relx=0.5, rely=0.5, anchor="center", 
                             relwidth=0.7, relheight=0.7)  # 15% margins on all sides
    
    def setup_bindings(self):
        """Setup click event bindings"""
        # Track clicks for double-click detection
        self.last_click_time = 0
        self.click_threshold = 500  # milliseconds for double-click
        
        def handle_click(event):
            current_time = time.time() * 1000  # Convert to milliseconds
            
            # Check if this is a double-click
            if current_time - self.last_click_time < self.click_threshold:
                self.reset_timer()
            else:
                # Schedule single-click action after threshold to ensure it's not a double-click
                self.root.after(self.click_threshold, lambda: self.toggle_timer() if time.time() * 1000 - current_time >= self.click_threshold else None)
            
            self.last_click_time = current_time
        
        # Bind click events to both the window and the label
        self.root.bind("<Button-1>", handle_click)
        self.time_label.bind("<Button-1>", handle_click)
        
        # Override the dragging for the label to prevent conflicts
        self.time_label.bind("<B1-Motion>", lambda event: self.root.event_generate("<B1-Motion>", x=event.x, y=event.y))
    
    def toggle_timer(self):
        """Toggle between start and pause states"""
        if self.running:
            self.pause_timer()
        else:
            self.start_timer()
    
    def start_timer(self):
        """Start the stopwatch"""
        if not self.running:
            self.running = True
            self.start_time = time.time() - self.elapsed_time
            # Keep text color white when running
            self.time_label.configure(fg="white")
    
    def pause_timer(self):
        """Pause the stopwatch"""
        if self.running:
            self.running = False
            if self.start_time > 0:
                self.elapsed_time = time.time() - self.start_time
            # Keep text color white when paused
            self.time_label.configure(fg="white")
    
    def reset_timer(self):
        """Reset the stopwatch to 00:00"""
        self.running = False
        self.elapsed_time = 0.0
        self.start_time = 0.0
        # Keep text color white
        self.time_label.configure(fg="white")
        self.update_time_display()
    
    def update_display(self):
        """Update the time display continuously"""
        self.update_time_display()
        # Schedule next update
        self.root.after(100, self.update_display)  # Update every 100ms for smooth display
    
    def update_time_display(self):
        """Update the displayed time"""
        if self.running and self.start_time > 0:
            current_elapsed = time.time() - self.start_time
        else:
            current_elapsed = self.elapsed_time
        
        # Convert to hours and minutes
        total_minutes = int(current_elapsed // 60)
        hours = total_minutes // 60
        minutes = total_minutes % 60
        
        # Format as HH:MM
        time_text = f"{hours:02d}:{minutes:02d}"
        self.time_label.configure(text=time_text)
    
    def run(self):
        """Start the application"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.root.quit()

def main():
    """Main entry point"""
    app = StopwatchWidget()
    app.run()

if __name__ == "__main__":
    main()
