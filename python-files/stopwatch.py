import tkinter as tk
from tkinter import ttk, simpledialog
from threading import Timer
import time

class StopwatchWidget:
    def __init__(self):
        # Initialize timer variables
        self.start_time = 0.0
        self.elapsed_time = 0.0
        self.running = False
        self.timer_thread = None
        self.is_countdown = False
        self.countdown_duration = 0.0
        self.current_opacity = 0.4
        
        # Create main window
        self.root = tk.Tk()
        self.setup_window()
        self.setup_display()
        self.setup_bindings()
        self.setup_context_menu()
        
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
        
        # Set transparency (40% opacity) - store current opacity
        self.current_opacity = 0.4
        self.root.attributes("-alpha", self.current_opacity)
        
        # Set background color to black
        self.root.configure(bg="black")
        
        # Add rounded corners effect by creating a frame with padding
        try:
            # Create a rounded effect visually with border radius simulation
            self.root.configure(relief="flat", borderwidth=0)
        except:
            pass
        
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
        self.is_dragging = False
        
        def start_drag(event):
            self.drag_start_x = event.x
            self.drag_start_y = event.y
            self.is_dragging = False
        
        def do_drag(event):
            self.is_dragging = True
            x = self.root.winfo_x() + event.x - self.drag_start_x
            y = self.root.winfo_y() + event.y - self.drag_start_y
            self.root.geometry(f"+{x}+{y}")
        
        # Bind dragging events
        self.root.bind("<ButtonPress-1>", start_drag)
        self.root.bind("<B1-Motion>", do_drag)
    
    def setup_display(self):
        """Create the time display label"""
        self.time_label = tk.Label(
            self.root,
            text="00:00",
            font=("Arial", 17, "bold"),  # Larger font size as requested
            fg="white",  # Full white text color at 100% opacity
            bg="black",  # Black background color
            anchor="center"
        )
        
        # Center the label in the window with 15% margins
        self.time_label.place(relx=0.5, rely=0.5, anchor="center", 
                             relwidth=0.7, relheight=0.7)  # 15% margins on all sides
    
    def setup_bindings(self):
        """Setup click event bindings"""
        # Track clicks for multi-click detection
        self.left_click_count = 0
        self.right_click_count = 0
        self.last_left_click_time = 0
        self.last_right_click_time = 0
        self.click_threshold = 400  # milliseconds for multi-click detection
        
        def handle_left_click(event):
            # Ignore if this was a drag operation
            if hasattr(self, 'is_dragging') and self.is_dragging:
                return
                
            current_time = time.time() * 1000
            
            # Reset count if too much time has passed
            if current_time - self.last_left_click_time > self.click_threshold:
                self.left_click_count = 0
            
            self.left_click_count += 1
            self.last_left_click_time = current_time
            
            # Schedule action after threshold to detect complete click sequence
            self.root.after(self.click_threshold, lambda: self.process_left_clicks())
        
        def handle_right_click(event):
            current_time = time.time() * 1000
            
            # Reset count if too much time has passed
            if current_time - self.last_right_click_time > self.click_threshold:
                self.right_click_count = 0
            
            self.right_click_count += 1
            self.last_right_click_time = current_time
            
            # Schedule action after threshold to detect complete click sequence
            self.root.after(self.click_threshold, lambda: self.process_right_clicks())
        
        def process_left_clicks():
            if self.left_click_count == 2:  # Only double click - toggle start/stop
                self.toggle_timer()
            elif self.left_click_count >= 3:  # Triple click or more - reset
                self.reset_timer()
            # Single click does nothing
            
            self.left_click_count = 0
        
        def process_right_clicks():
            if self.right_click_count == 1:  # Single right click - show context menu
                self.show_context_menu()
            elif self.right_click_count >= 2:  # Double right click or more - reset
                self.reset_timer()
            
            self.right_click_count = 0
        
        self.process_left_clicks = process_left_clicks
        self.process_right_clicks = process_right_clicks
        
        # Bind click events to both the window and the label
        self.root.bind("<ButtonRelease-1>", handle_left_click)  # Use ButtonRelease to avoid conflict with drag
        self.time_label.bind("<ButtonRelease-1>", handle_left_click)
        
        # Bind right-click to show context menu immediately on single click
        def show_menu_on_right_click(event):
            self.show_context_menu()
        
        self.root.bind("<Button-3>", show_menu_on_right_click)  # Right click
        self.time_label.bind("<Button-3>", show_menu_on_right_click)
        
        # Override the dragging for the label to prevent conflicts
        self.time_label.bind("<ButtonPress-1>", lambda event: setattr(self, 'is_dragging', False))
        self.time_label.bind("<B1-Motion>", lambda event: (setattr(self, 'is_dragging', True), self.root.event_generate("<B1-Motion>", x=event.x, y=event.y)))
    
    def setup_context_menu(self):
        """Setup right-click context menu"""
        self.context_menu = tk.Menu(self.root, tearoff=0, bg="black", fg="white", 
                                   activebackground="gray", activeforeground="white")
        
        # Add timer options
        self.context_menu.add_command(label="15 min", command=lambda: self.start_countdown(15))
        self.context_menu.add_command(label="30 min", command=lambda: self.start_countdown(30))
        self.context_menu.add_command(label="45 min", command=lambda: self.start_countdown(45))
        self.context_menu.add_command(label="60 min", command=lambda: self.start_countdown(60))
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Custom", command=self.start_custom_countdown)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Stopwatch", command=self.switch_to_stopwatch)
    
    def show_context_menu(self):
        """Show the context menu at current mouse position"""
        try:
            x = self.root.winfo_pointerx()
            y = self.root.winfo_pointery()
            self.context_menu.post(x, y)
        except:
            pass
    
    def start_countdown(self, minutes):
        """Start countdown timer for specified minutes"""
        self.is_countdown = True
        self.countdown_duration = minutes * 60  # Convert to seconds
        self.elapsed_time = 0.0
        self.running = True
        self.start_time = time.time()
        # Set opacity to 40% when running
        self.current_opacity = 0.4
        self.root.attributes("-alpha", self.current_opacity)
        # White text when running
        self.time_label.configure(fg="white")
    
    def start_custom_countdown(self):
        """Start custom countdown timer"""
        try:
            # Create a custom dialog window
            dialog = tk.Toplevel(self.root)
            dialog.title("Timer")
            dialog.geometry("200x120")
            dialog.configure(bg="black")
            dialog.attributes("-topmost", True)
            dialog.resizable(False, False)
            
            # Center the dialog
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() - 200) // 2
            y = (dialog.winfo_screenheight() - 120) // 2
            dialog.geometry(f"200x120+{x}+{y}")
            
            # Add label
            label = tk.Label(dialog, text="Enter minutes:", 
                           font=("Arial", 10), fg="white", bg="black")
            label.pack(pady=10)
            
            # Add entry
            entry = tk.Entry(dialog, font=("Arial", 12), width=10, justify='center')
            entry.pack(pady=5)
            entry.focus_set()
            
            # Add buttons frame
            button_frame = tk.Frame(dialog, bg="black")
            button_frame.pack(pady=10)
            
            def on_ok():
                try:
                    minutes = int(entry.get())
                    if 1 <= minutes <= 999:
                        dialog.destroy()
                        self.start_countdown(minutes)
                    else:
                        entry.delete(0, tk.END)
                        entry.insert(0, "1-999 only")
                except ValueError:
                    entry.delete(0, tk.END)
                    entry.insert(0, "Numbers only")
            
            def on_cancel():
                dialog.destroy()
            
            # OK button
            ok_btn = tk.Button(button_frame, text="OK", command=on_ok,
                             bg="gray", fg="white", width=6)
            ok_btn.pack(side=tk.LEFT, padx=5)
            
            # Cancel button
            cancel_btn = tk.Button(button_frame, text="Cancel", command=on_cancel,
                                 bg="gray", fg="white", width=6)
            cancel_btn.pack(side=tk.LEFT, padx=5)
            
            # Bind Enter key
            entry.bind("<Return>", lambda e: on_ok())
            
        except:
            pass
    
    def switch_to_stopwatch(self):
        """Switch back to stopwatch mode"""
        self.is_countdown = False
        self.reset_timer()
    
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
            # Set window opacity to 40% when running
            self.current_opacity = 0.5
            self.root.attributes("-alpha", self.current_opacity)
            # Keep text color full white when running (100% opacity)
            self.time_label.configure(fg="white")
    
    def pause_timer(self):
        """Pause the stopwatch"""
        if self.running:
            self.running = False
            if self.start_time > 0:
                self.elapsed_time = time.time() - self.start_time
            # Set window opacity to 20% when paused (updated from 15%)
            self.current_opacity = 0.50
            self.root.attributes("-alpha", self.current_opacity)
            # Change text color to yellow when stopped/paused (100% opacity)
            self.time_label.configure(fg="yellow")
    
    def reset_timer(self):
        """Reset the stopwatch to 00:00"""
        self.running = False
        self.elapsed_time = 0.0
        self.start_time = 0.0
        self.is_countdown = False
        self.countdown_duration = 0.0
        # Set window opacity to 20% when reset (stopped state)
        self.current_opacity = 0.20
        self.root.attributes("-alpha", self.current_opacity)
        # Set text color to yellow when reset (stopped state, 100% opacity)
        self.time_label.configure(fg="yellow")
        self.update_time_display()
    
    def update_display(self):
        """Update the time display continuously"""
        self.update_time_display()
        # Schedule next update
        self.root.after(100, self.update_display)  # Update every 100ms for smooth display
    
    def update_time_display(self):
        """Update the displayed time"""
        if self.is_countdown:
            # Countdown timer logic
            if self.running and self.start_time > 0:
                elapsed = time.time() - self.start_time
                remaining = max(0, self.countdown_duration - elapsed)
                
                # Check if countdown finished
                if remaining <= 0:
                    self.running = False
                    self.current_opacity = 0.20
                    self.root.attributes("-alpha", self.current_opacity)
                    self.time_label.configure(fg="yellow")
                    remaining = 0
                
                current_elapsed = remaining
            else:
                current_elapsed = max(0, self.countdown_duration - self.elapsed_time)
        else:
            # Stopwatch logic
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
