
import tkinter as tk
import time
import math
import threading

class GalaxySimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulasi Alam Semesta ?? - Galaksi Bimasakti")

        self.canvas = tk.Canvas(root, width=900, height=700, bg="black")
        self.canvas.pack()

        # Kontrol
        control_frame = tk.Frame(root, bg="gray20")
        control_frame.pack(fill=tk.X)

        buttons = [
            ("Start", self.start),
            ("Stop", self.stop),
            ("Speed +", self.speed_up),
            ("Slow", self.slow_down),
            ("Zoom In", self.zoom_in),
            ("Zoom Out", self.zoom_out)
        ]
        for i, (text, command) in enumerate(buttons):
            tk.Button(control_frame, text=text, width=10, command=command).grid(row=0, column=i, padx=4, pady=5)

        # Inisialisasi properti
        self.running = False
        self.zoom = 1.0
        self.speed = 0.02
        self.angle = 0
        self.objects = []

        # Posisi pusat galaksi
        self.center_x = 450
        self.center_y = 350

        # Membuat objek benda langit
        self.create_objects()

    def create_objects(self):
        self.objects.clear()
        self.canvas.delete("all")

        # Matahari sebagai pusat
        self.sun = self.canvas.create_oval(self.center_x - 10, self.center_y - 10,
                                           self.center_x + 10, self.center_y + 10,
                                           fill="yellow")

        # Planet / bintang orbit: (radius, size, color, speed factor)
        self.orbit_objects = [
            (60, 4, "blue", 1.0),       # Bumi
            (100, 3, "red", 0.7),       # Mars
            (160, 6, "orange", 0.4),    # Jupiter
            (230, 4, "white", 0.25),    # Saturnus
            (300, 2, "cyan", 0.1),      # Uranus
            (380, 2, "pink", 0.05),     # Neptunus
            (450, 1, "gray", 0.03),     # Pluto
            (520, 1, "lightblue", 0.02),# Bintang luar
        ]

        for radius, size, color, _ in self.orbit_objects:
            obj = self.canvas.create_oval(0, 0, 0, 0, fill=color)
            self.objects.append((obj, radius, size, color))

    def update_positions(self):
        while self.running:
            self.angle += 1

            for i, (obj, radius, size, color) in enumerate(self.objects):
                orbit_speed = self.orbit_objects[i][3]
                angle = self.angle * orbit_speed

                # Orbit position
                x = self.center_x + math.cos(math.radians(angle)) * radius * self.zoom
                y = self.center_y + math.sin(math.radians(angle)) * radius * self.zoom

                # Update object
                self.canvas.coords(obj,
                    x - size * self.zoom, y - size * self.zoom,
                    x + size * self.zoom, y + size * self.zoom
                )

            self.canvas.update()
            time.sleep(self.speed)

    def start(self):
        if not self.running:
            self.running = True
            threading.Thread(target=self.update_positions, daemon=True).start()

    def stop(self):
        self.running = False

    def speed_up(self):
        if self.speed > 0.005:
            self.speed -= 0.005

    def slow_down(self):
        if self.speed < 0.2:
            self.speed += 0.005

    def zoom_in(self):
        self.zoom *= 1.1
        self.create_objects()  # Redraw objects to apply zoom

    def zoom_out(self):
        self.zoom *= 0.9
        self.create_objects()

if __name__ == "__main__":
    root = tk.Tk()
    app = GalaxySimulator(root)
    root.mainloop()
