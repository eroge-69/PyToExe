import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from datetime import datetime

kivy.require('2.3.0')

class CountdownApp(App):
    def build(self):
        # Create a vertical BoxLayout
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        # Background image of Earth from space
        with layout.canvas.before:
            Color(1, 1, 1, 0.2)  # Slight white tint for readability
            self.background = Rectangle(source='3.jpg', pos=layout.pos, size=layout.size)
            layout.bind(pos=self.update_background, size=self.update_background)
        
        # Red digital clock label
        self.red_clock_label = Label(
            text="CURRENT TIME: Calculating...",
            font_size='24sp',
            halign='center',
            valign='middle',
            color=(1, 0, 0, 1),  # Red color
            bold=True,
            outline_color=(0, 0, 1, 1),  # Blue outline for contrast
            outline_width=2,
            size_hint=(1, 0.4)  # Increased to use more space
        )
        layout.add_widget(self.red_clock_label)
        
        # Countdown label
        self.countdown_label = Label(
            text="TIME UNTIL NOVEMBER 10, 2025, 08:00:00 AM:\nCalculating...",
            font_size='22sp',
            halign='center',
            valign='middle',
            color=(1, 0.5, 0, 1),  # Orange for contrast
            bold=True,
            size_hint=(1, 0.6)  # Increased to use remaining space
        )
        layout.add_widget(self.countdown_label)
        
        # Schedule the update function to run every second
        Clock.schedule_interval(self.update_display, 1)
        
        return layout

    def update_background(self, instance, value):
        self.background.pos = instance.pos
        self.background.size = instance.size

    def update_display(self, dt):
        # Get current time from device
        current_date = datetime.now()
        
        # Update red digital clock
        self.red_clock_label.text = f"CURRENT TIME: {current_date.strftime('%Y-%m-%d %H:%M:%S %Z')}".upper()
        
        # Target date and time
        target_date = datetime(2025, 11, 10, 8, 0, 0)
        
        # Check if target date has passed
        if current_date >= target_date:
            self.countdown_label.text = "COUNTDOWN COMPLETE!"
            Clock.unschedule(self.update_display)  # Stop updating
            return
        
        # Calculate the time difference
        time_diff = target_date - current_date
        
        # Extract days, hours, minutes, and seconds
        days = time_diff.days
        seconds = time_diff.seconds
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        
        # Update the countdown label
        self.countdown_label.text = (
            f"TIME UNTIL NOVEMBER 10, 2025, 08:00:00 AM:\n"
            f"{days} DAYS, {hours:02d} HOURS, {minutes:02d} MINUTES, {seconds:02d} SECONDS"
        ).upper()

if __name__ == '__main__':
    CountdownApp().run()
