import time
import tkinter as tk
import pygame
import os
import math

class ClockReminderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Clock Reminder")
        self.root.configure(bg='black')
        self.root.geometry("300x300")  # Initial size
        self.root.resizable(True, True)  # Allow resizing
        self.root.attributes('-topmost', True)  # Keep window on top

        # Initialize pygame mixer
        pygame.mixer.init()
        self.sound_file = "default_beep.mp3"  # Default sound file
        self.reminded_minutes = set()  # Track reminded minutes

        # Create canvas for analog clock
        self.canvas = tk.Canvas(root, bg='black', highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)

        # Bind resize event to redraw clock
        self.canvas.bind("<Configure>", self.resize_clock)

        # Initialize clock elements
        self.clock_center = None
        self.clock_radius = None
        self.hour_hand = None
        self.minute_hand = None

        # Force initial draw after a short delay to ensure canvas is ready
        self.root.after(100, self.initial_draw)

        # Start clock and reminder updates
        self.update_clock()
        self.check_reminder()

    def play_sound(self):
        """Play the reminder sound"""
        try:
            pygame.mixer.music.load(self.sound_file)
            pygame.mixer.music.play()
        except pygame.error as e:
            print(f"Cannot play audio: {e}. Ensure default_beep.mp3 is a valid .mp3 file.")

    def draw_clock(self, width, height):
        """Draw the analog clock with gold hour and minute hands"""
        self.canvas.delete("all")  # Clear previous drawings

        # Calculate clock center and radius
        self.clock_center = (width / 2, height / 2)
        self.clock_radius = min(width, height) * 0.4

        # Draw clock face (black background, no border or numbers)
        self.canvas.create_oval(
            self.clock_center[0] - self.clock_radius,
            self.clock_center[1] - self.clock_radius,
            self.clock_center[0] + self.clock_radius,
            self.clock_center[1] + self.clock_radius,
            fill='black', outline='black'
        )

        # Get current time
        current_time = time.localtime()
        hour = current_time.tm_hour % 12
        minute = current_time.tm_min

        # Calculate angles for hour and minute hands
        hour_angle = math.radians((hour % 12 + minute / 60) * 30 - 90)
        minute_angle = math.radians(minute * 6 - 90)

        # Hour hand (shorter, thicker, gold)
        hour_hand_length = self.clock_radius * 0.5
        hour_x = self.clock_center[0] + hour_hand_length * math.cos(hour_angle)
        hour_y = self.clock_center[1] + hour_hand_length * math.sin(hour_angle)
        self.hour_hand = self.canvas.create_line(
            self.clock_center[0], self.clock_center[1], hour_x, hour_y,
            fill='gold', width=4
        )

        # Minute hand (longer, thinner, gold)
        minute_hand_length = self.clock_radius * 0.8
        minute_x = self.clock_center[0] + minute_hand_length * math.cos(minute_angle)
        minute_y = self.clock_center[1] + minute_hand_length * math.sin(minute_angle)
        self.minute_hand = self.canvas.create_line(
            self.clock_center[0], self.clock_center[1], minute_x, minute_y,
            fill='gold', width=2
        )

    def initial_draw(self):
        """Force initial clock draw after canvas is ready"""
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        if width > 1 and height > 1:  # Ensure canvas is initialized
            self.draw_clock(width, height)

    def resize_clock(self, event):
        """Redraw clock on window resize"""
        self.draw_clock(event.width, event.height)

    def update_clock(self):
        """Update the analog clock display"""
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        if width > 1 and height > 1:  # Ensure canvas is initialized
            self.draw_clock(width, height)
        self.root.after(1000, self.update_clock)  # Update every second

    def check_reminder(self):
        """Check if a reminder is needed"""
        current_time = time.localtime()
        current_hour = current_time.tm_hour
        current_minute = current_time.tm_min

        # Reset reminded_minutes when entering a new hour
        if current_minute == 0 and len(self.reminded_minutes) > 0:
            self.reminded_minutes.clear()

        # Check for reminders at 0, 15, 30, 45 minutes
        if current_minute in [0, 15, 30, 45] and current_minute not in self.reminded_minutes:
            print(f"Reminder: {current_hour:02d}:{current_minute:02d}")
            self.play_sound()
            self.reminded_minutes.add(current_minute)

        # Check every second
        self.root.after(1000, self.check_reminder)

if __name__ == "__main__":
    # Check for default sound file
    if not os.path.exists("default_beep.mp3"):
        print("Error: default_beep.mp3 not found. Please place a valid .mp3 file in the directory.")
        exit(1)

    root = tk.Tk()
    app = ClockReminderApp(root)
    root.mainloop()