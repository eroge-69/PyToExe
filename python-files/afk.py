import customtkinter as ctk
import threading
import random
import time
from pynput.keyboard import Controller as KeyboardController, Key
from pynput.mouse import Controller as MouseController

# Initialize input controllers
keyboard = KeyboardController()
mouse = MouseController()

# Globals
running = False
delay_minutes = 5

# GUI app
class AntiAFKApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Anti-AFK Script")
        self.geometry("400x300")
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        # Input for minutes
        self.delay_label = ctk.CTkLabel(self, text="AFK Delay (minutes):")
        self.delay_label.pack(pady=(20, 5))
        self.delay_input = ctk.CTkEntry(self)
        self.delay_input.insert(0, "5")
        self.delay_input.pack()

        # Toggles
        self.space_enabled = ctk.CTkCheckBox(self, text="Enable Spacebar")
        self.space_enabled.pack(pady=5)
        self.numbers_enabled = ctk.CTkCheckBox(self, text="Enable Numbers (0-9)")
        self.numbers_enabled.pack(pady=5)
        self.wasd_enabled = ctk.CTkCheckBox(self, text="Enable WASD Movement")
        self.wasd_enabled.pack(pady=5)
        self.mouse_enabled = ctk.CTkCheckBox(self, text="Enable Mouse Movement")
        self.mouse_enabled.pack(pady=5)

        # Start/Stop button
        self.toggle_button = ctk.CTkButton(self, text="Start", command=self.toggle_script)
        self.toggle_button.pack(pady=20)

    def toggle_script(self):
        global running
        running = not running

        if running:
            self.toggle_button.configure(text="Stop")
            thread = threading.Thread(target=self.run_script)
            thread.daemon = True
            thread.start()
        else:
            self.toggle_button.configure(text="Start")

    def run_script(self):
        global running
        try:
            delay = float(self.delay_input.get())
        except ValueError:
            delay = 5  # fallback
        while running:
            time.sleep(delay * 60)

            if not running:
                break

            keys = []
            if self.wasd_enabled.get():
                keys += ['w', 'a', 's', 'd']
            if self.numbers_enabled.get():
                keys += [str(n) for n in range(10)]
            if not keys:
                keys += ['q', 'e', 'r', 't', 'y']

            key = random.choice(keys)

            if self.space_enabled.get():
                keyboard.press(Key.space)
                keyboard.press(key)
                keyboard.release(key)
                keyboard.release(Key.space)
            else:
                keyboard.press(key)
                keyboard.release(key)

            if self.mouse_enabled.get():
                x, y = mouse.position
                dx = random.randint(-5, 5)
                dy = random.randint(-5, 5)
                mouse.move(dx, dy)

if __name__ == "__main__":
    app = AntiAFKApp()
    app.mainloop()
