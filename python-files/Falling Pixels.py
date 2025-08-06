import tkinter as tk
import random

# Constants
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 900
NUM_PIXELS = 250
PIXEL_SIZE = 5
SPEED_X = 9 # Speed to the left
SPEED_Y = 0  # Speed downward
FRAME_DELAY = 30  # Milliseconds between frames

class PixelRain:
    def __init__(self):
        # Create window
        self.root = tk.Tk()
        self.root.title("Falling Pixels")
        self.root.resizable(False, False)

        # Create canvas
        self.canvas = tk.Canvas(self.root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, bg="black", highlightthickness=0)
        self.canvas.pack()

        # Create pixels
        self.pixels = []
        for _ in range(NUM_PIXELS):
            x = random.randint(0, WINDOW_WIDTH)
            y = random.randint(0, WINDOW_HEIGHT)
            pixel = self.canvas.create_rectangle(x, y, x + PIXEL_SIZE, y + PIXEL_SIZE, fill="white", outline="")
            self.pixels.append(pixel)

        # Start animation
        self.animate()
        self.root.mainloop()

    def animate(self):
        for pixel in self.pixels:
            x1, y1, x2, y2 = self.canvas.coords(pixel)

            # Move pixel left and down
            self.canvas.move(pixel, -SPEED_X, SPEED_Y)

            # If pixel leaves the screen, reset it to right at random height
            if x2 < 0 or y1 > WINDOW_HEIGHT:
                new_x = WINDOW_WIDTH + random.randint(0, 100)
                new_y = random.randint(0, WINDOW_HEIGHT)
                self.canvas.coords(pixel, new_x, new_y, new_x + PIXEL_SIZE, new_y + PIXEL_SIZE)

        self.canvas.after(FRAME_DELAY, self.animate)

# Run the program
if __name__ == "__main__":
    PixelRain()
