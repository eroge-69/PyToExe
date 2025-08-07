from turtle import *
import colorsys

# Set the speed of drawing and background color
speed(0)
bgcolor("black")

# Initialize hue value
h = 0

# Outer loop for 16 repetitions
for i in range(16):
    # Inner loop for drawing 18 shapes
    for j in range(18):
        # Get the color using HSV to RGB conversion
        c = colorsys.hsv_to_rgb(h, 1, 1)
        color(c)

        # Increment hue for the next color
        h += 0.005
        
        # Draw shapes
        right(90)
        circle(150 - j * 6, 90)
        left(90)
        circle(150 - j * 6, 90)
        right(180)
        circle(40, 24)

# Complete the drawing
done()