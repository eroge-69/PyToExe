import tkinter as tk
import time

class StopwatchWidget:
    def __init__(self):
        # Initialize timer variables
        self.start_time = 0.0
        self.elapsed_time = 0.0
        self.running = False
        
        # Click/Drag detection variables
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.is_dragging = False # Flag to indicate if a drag operation is active
        self.click_threshold_ms = 400  # milliseconds for multi-click detection
        self.drag_detection_threshold = 5 # pixels: movement beyond this is considered a drag
        
        # Variables for multi-click detection
        self.left_click_count = 0
        self.last_left_click_time = 0
        self.left_click_after_id = None # Stores the ID of the 'after' call for click processing
        
        # Variable for double right-click detection
        self.last_right_click_time = 0
        
        # Create main window
        self.root = tk.Tk()
        self.setup_window()
        self.setup_display()
        self.setup_bindings()
        
        # Start the update loop that continuously refreshes the display
        self.update_display()
    
    def setup_window(self):
        """Configure the main window properties."""
        # Remove standard title bar for a minimalist look
        self.root.overrideredirect(True)
        # Prevent window resizing
        self.root.resizable(False, False)
        
        # Set fixed window size
        self.root.geometry("100x40")
        
        # Keep the window always on top of other applications
        self.root.attributes("-topmost", True)
        
        # Set initial window transparency (40% opacity)
        self.root.attributes("-alpha", 0.4)
        
        # Set background color to black
        self.root.configure(bg="black")
        
        # Center the window on the screen
        self.center_window()
    
    def center_window(self):
        """Center the window on the screen."""
        # Update geometry to get correct window dimensions
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Calculate x and y coordinates to center the window
        x = (screen_width - 100) // 2
        y = (screen_height - 40) // 2
        
        self.root.geometry(f"100x40+{x}+{y}")
    
    def setup_display(self):
        """Create the time display label."""
        self.time_label = tk.Label(
            self.root,
            text="00:00", # Initial text display
            font=("Arial", 17, "bold"),  # Larger and bold font
            fg="yellow",  # Initial text color is yellow (matching reset/paused state)
            bg="black",   # Black background for the label
            anchor="center" # Center the text within the label
        )
        
        # Position the label in the center of the window with relative sizing (15% margins)
        self.time_label.place(relx=0.5, rely=0.5, anchor="center", 
                              relwidth=0.7, relheight=0.7)
    
    def setup_bindings(self):
        """Setup comprehensive click and drag event bindings for the entire window and label."""
        
        def on_mouse_button_press(event):
            """Handles mouse button press events."""
            # Store initial position of the mouse for drag detection
            self.drag_start_x = event.x
            self.drag_start_y = event.y
            self.is_dragging = False # Assume it's a click initially, until significant movement occurs
            
            # If it's a left mouse button press (Button-1)
            if event.num == 1: 
                current_time_ms = time.time() * 1000
                
                # If a previous 'after' call for click processing exists, cancel it.
                # This is crucial for accurate multi-click detection.
                if self.left_click_after_id:
                    self.root.after_cancel(self.left_click_after_id)
                
                # Reset click count if the time elapsed since the last click is too long
                if current_time_ms - self.last_left_click_time > self.click_threshold_ms:
                    self.left_click_count = 0
                
                self.left_click_count += 1
                self.last_left_click_time = current_time_ms
                
                # Schedule 'process_left_clicks' to run after a short delay.
                # This 'after' call will be cancelled if a drag is subsequently detected,
                # ensuring that drags do not trigger click actions.
                self.left_click_after_id = self.root.after(self.click_threshold_ms, self.process_left_clicks)
            
            # If it's a right mouse button press (Button-3)
            elif event.num == 3: 
                current_time_ms = time.time() * 1000
                # Check for a double right-click within the threshold
                if current_time_ms - self.last_right_click_time < self.click_threshold_ms:
                    self.reset_timer()  # Double right-click resets the stopwatch
                self.last_right_click_time = current_time_ms

        def on_mouse_motion(event):
            """Handles mouse motion events, used for dragging detection and execution."""
            # Check if the left mouse button (Button-1) is currently held down during motion
            # event.state & 0x0100 is the bitmask for Button-1 being pressed
            if event.state & 0x0100: 
                # If we haven't yet identified this interaction as a drag
                if not self.is_dragging:
                    # Calculate horizontal and vertical movement from the initial press point
                    dx = abs(event.x - self.drag_start_x)
                    dy = abs(event.y - self.drag_start_y)
                    
                    # If movement exceeds the drag detection threshold, it's a drag
                    if dx > self.drag_detection_threshold or dy > self.drag_detection_threshold:
                        self.is_dragging = True # Set the dragging flag
                        # Crucially, if a drag starts, cancel any pending click actions
                        # This prevents the initial press from being misinterpreted as a click
                        if self.left_click_after_id:
                            self.root.after_cancel(self.left_click_after_id)
                            self.left_click_after_id = None # Clear the ID
                        self.left_click_count = 0 # Reset click count, as this is now a drag, not a click
                
                # If it has been identified as a drag, move the window
                if self.is_dragging:
                    # Calculate new window position based on mouse movement
                    x = self.root.winfo_x() + event.x - self.drag_start_x
                    y = self.root.winfo_y() + event.y - self.drag_start_y
                    self.root.geometry(f"+{x}+{y}")
        
        def on_mouse_button_release(event):
            """Handles mouse button release events."""
            # Reset the dragging flag when any mouse button is released
            self.is_dragging = False
            # No explicit action needed for left button release here, as click processing
            # is handled by the scheduled 'after' call in on_mouse_button_press.
            # Right click is handled on press for double-click detection.
            pass
            

        # Bind event handlers to both the root window and the time_label
        # Binding to root ensures events are caught even if user clicks/drags outside the label
        self.root.bind("<ButtonPress>", on_mouse_button_press) # Binds to any button press
        self.root.bind("<B1-Motion>", on_mouse_motion)       # Binds to left button motion
        self.root.bind("<ButtonRelease>", on_mouse_button_release) # Binds to any button release
        
        # Also bind to the time_label to ensure clicks/drags originating directly on it are caught
        self.time_label.bind("<ButtonPress>", on_mouse_button_press)
        self.time_label.bind("<B1-Motion>", on_mouse_motion)
        self.time_label.bind("<ButtonRelease>", on_mouse_button_release)
    
    def process_left_clicks(self):
        """
        Processes the accumulated left clicks after the click_threshold has passed.
        This function is called by 'root.after' and determines if a double or triple click occurred.
        Single clicks are explicitly ignored.
        """
        # Ensure this function only proceeds if the 'after' call was not cancelled (e.g., by a drag)
        if self.left_click_after_id is not None:
            if self.left_click_count == 2:  # Double click detected
                self.toggle_timer() # Toggle the stopwatch state
            elif self.left_click_count >= 3:  # Triple click (or more) detected
                self.reset_timer() # Reset the stopwatch
            # If left_click_count is 1, no action is taken, effectively disabling single clicks.
        
        # Reset click count and the 'after' ID for the next sequence of clicks
        self.left_click_count = 0
        self.left_click_after_id = None
    
    def toggle_timer(self):
        """Toggles the stopwatch between running and paused states."""
        if self.running:
            self.pause_timer()
        else:
            self.start_timer()
    
    def start_timer(self):
        """Starts the stopwatch."""
        if not self.running:
            self.running = True
            # Calculate start_time to account for any previously elapsed time (if resuming)
            self.start_time = time.time() - self.elapsed_time
            # Set window opacity to 50% when the timer is running
            self.root.attributes("-alpha", 0.5)
            # Set text color to white when running
            self.time_label.configure(fg="white")
    
    def pause_timer(self):
        """Pauses the stopwatch."""
        if self.running:
            self.running = False
            # If timer was running, record the elapsed time up to this point
            if self.start_time > 0:
                self.elapsed_time = time.time() - self.start_time
            # Set window opacity to 50% when paused
            self.root.attributes("-alpha", 0.5)
            # Change text color to yellow when paused
            self.time_label.configure(fg="yellow")
    
    def reset_timer(self):
        """Resets the stopwatch to 00:00."""
        self.running = False
        self.elapsed_time = 0.0
        self.start_time = 0.0
        # Set window opacity back to initial 40% when reset
        self.root.attributes("-alpha", 0.4)
        # Set text color to yellow when reset
        self.time_label.configure(fg="yellow")
        # Immediately update the display to show 00:00
        self.update_time_display()
    
    def update_display(self):
        """Continuously updates the time display."""
        self.update_time_display()
        # Schedule the next update to happen every 100 milliseconds for smooth display
        self.root.after(100, self.update_display)
    
    def update_time_display(self):
        """Calculates and updates the displayed time."""
        if self.running and self.start_time > 0:
            current_elapsed = time.time() - self.start_time
        else:
            current_elapsed = self.elapsed_time
        
        # Convert total elapsed seconds into hours and minutes for display
        total_minutes = int(current_elapsed // 60)
        hours = total_minutes // 60
        minutes = total_minutes % 60
        
        # Format the time as HH:MM with leading zeros
        time_text = f"{hours:02d}:{minutes:02d}"
        self.time_label.configure(text=time_text)
    
    def run(self):
        """Starts the application's main loop."""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully if the script is run from a console
            self.root.quit()

def main():
    """Main entry point for the stopwatch application."""
    app = StopwatchWidget()
    app.run()

if __name__ == "__main__":
    main()

