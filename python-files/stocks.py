import io
import urllib.request
from turtle import Screen, Turtle, done, colormode
from PIL import Image
import time

# === SETTINGS ===
image_url = "https://i.postimg.cc/2Smky5Kr/Screenshot-2025-06-28-143437-removebg-preview.png"  # put your image link here
scale = 6                 # pixel size
window_width = 800
window_height = 600
padding = 20
turtle_speed = 3          # 1-10, slower = more visible movement
line_delay = 0.001        # delay between drawing pixels for visible strokes

# === DOWNLOAD IMAGE ===
print("Downloading image...")
with urllib.request.urlopen(image_url) as response:
    image_data = response.read()

img = Image.open(io.BytesIO(image_data)).convert("RGBA")
orig_w, orig_h = img.size

# === SCALE IMAGE TO FIT WINDOW ===
max_w = (window_width - padding) // scale
max_h = (window_height - padding) // scale
scale_factor = min(max_w / orig_w, max_h / orig_h, 1)
new_w = max(1, int(orig_w * scale_factor))
new_h = max(1, int(orig_h * scale_factor))
img = img.resize((new_w, new_h), Image.NEAREST)
w, h = img.size
pixels = img.load()

# === TURTLE SETUP ===
screen = Screen()
screen.setup(width=window_width, height=window_height)
screen.bgcolor("white")
colormode(255)

t = Turtle()
t.hideturtle()
t.speed(turtle_speed)
t.penup()

start_x = - (w*scale) / 2
start_y = (h*scale) / 2
screen.tracer(0)

# === DRAW IMAGE LIKE AN ARTIST ===
for y in range(h):
    x = 0
    while x < w:
        r, g, b, a = pixels[x, y]
        if a == 0:
            x += 1
            continue

        # Start a stroke for consecutive same-color pixels
        stroke_color = (r, g, b)
        t.penup()
        t.goto(start_x + x*scale, start_y - y*scale)
        t.pendown()
        while x < w:
            r2, g2, b2, a2 = pixels[x, y]
            if a2 == 0 or (r2, g2, b2) != stroke_color:
                break
            t.dot(scale, stroke_color)
            t.forward(0)  # keep pen down to see the stroke effect
            x += 1
            time.sleep(line_delay)
        t.penup()
    if y % 5 == 0:
        screen.update()

screen.update()
done()
