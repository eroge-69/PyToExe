import os
os.environ['TCL_LIBRARY'] = r'C:\Users\SeCu797\AppData\Local\Programs\Python\Python313\tcl\tcl8.6'
import turtle
import math
import time

screen = turtle.Screen()
screen.bgcolor("ghostwhite")
screen.title("Rolling Ball with Centered HP Text and Typewriter Farewell")
screen.tracer(0)

ball = turtle.Turtle()
ball.hideturtle()
ball.penup()

letters = turtle.Turtle()
letters.hideturtle()
letters.penup()
letters.speed(0)

separator = turtle.Turtle()
separator.hideturtle()
separator.penup()
separator.speed(0)

# Turtle for the farewell message behind the ball
text_turtle = turtle.Turtle()
text_turtle.hideturtle()
text_turtle.penup()
text_turtle.color("slategrey")

ball_radius = 30
ground_y = -50
y = ground_y + ball_radius  # ball center y position exactly radius above ground line
start_x = -250
end_x = 250
step = 4  # Slower step for smoother rolling
angle = 0

shear = 0.3  # Italic slant

def shear_point(x, y, s):
    return x + s * y, y

def rotate_point(x, y, rad):
    cos_r = math.cos(rad)
    sin_r = math.sin(rad)
    return x * cos_r - y * sin_r, x * sin_r + y * cos_r

def draw_poly(t, pts):
    t.penup()
    t.goto(pts[0])
    t.pendown()
    t.begin_fill()
    for p in pts[1:]:
        t.goto(p)
    t.goto(pts[0])
    t.end_fill()
    t.penup()

# Letter shapes centered near origin (original coords)
H_left = [(-25, 20), (-20, 20), (-20, -20), (-25, -20)]
H_right = [(-5, 20), (0, 20), (0, -20), (-5, -20)]
H_cross = [(-20, 5), (-5, 5), (-5, 0), (-20, 0)]

P_vert = [(5, 20), (10, 20), (10, -20), (5, -20)]
P_outer_top = [(10, 20), (25, 20), (30, 15), (30, 5), (25, 0), (10, 0)]
P_inner_hole = [
    (17, 15), (22, 15), (27, 10), (27, 6), (22, 1), (17, 1)
]

letters.color("#0096D6")
letters.pensize(3)

# Adjust offsets to center HP group better inside ball (moved left and down a bit)
x_offset = -10
y_offset = 8

# Hollow gap inside P is shifted slightly relative to other parts
hole_x_adjust = -1.5
hole_y_adjust = 0.5

# White vertical separator between H and P (before transform)
separator_rect = [
    (0, 22),  # top-left
    (3, 22),  # top-right
    (3, -22), # bottom-right
    (0, -22)  # bottom-left
]

def draw_HP_group(t, cx, cy, angle_deg):
    rad = math.radians(angle_deg)
    scale = 0.5  # your chosen scale

    def transform_points(poly, shift_hole=False):
        transformed = []
        for (x, y) in poly:
            # Apply centering offset
            x -= x_offset
            y -= y_offset

            # Adjust hole position if needed
            if shift_hole:
                x += hole_x_adjust
                y += hole_y_adjust

            # Shear (italic)
            sx, sy = shear_point(x, y, shear)

            # Scale
            sx *= scale
            sy *= scale

            # Rotate
            rx, ry = rotate_point(sx, sy, rad)

            # Translate to center position on ball
            tx, ty = rx + cx, ry + cy

            transformed.append((tx, ty))
        return transformed

    # Draw H parts
    for poly in [H_left, H_right, H_cross]:
        draw_poly(t, transform_points(poly))

    # Draw P parts (outer)
    draw_poly(t, transform_points(P_outer_top))
    draw_poly(t, transform_points(P_vert))

    # Draw hollow hole inside P with white fill and adjusted position
    transformed_hole = transform_points(P_inner_hole, shift_hole=True)
    t_white = turtle.Turtle()
    t_white.hideturtle()
    t_white.penup()
    t_white.color("ghostwhite")
    t_white.pensize(0)
    t_white.speed(0)
    draw_poly(t_white, transformed_hole)

    # Draw white vertical separator line between H and P
    transformed_sep = transform_points(separator_rect)
    separator.clear()
    separator.color("white")
    separator.pensize(0)
    draw_poly(separator, transformed_sep)

# Farewell message for typewriter effect
farewell_msg = "Thank you everyone for the wonderful internship!"
total_letters = len(farewell_msg)
total_distance = end_x - start_x

for x in range(start_x, end_x + step, step):
    ball.clear()
    letters.clear()
    separator.clear()
    text_turtle.clear()

    # Draw ground line
    ball.goto(-300, ground_y)
    ball.pendown()
    ball.forward(600)
    ball.penup()

    # Draw ball (bottom at ground_y)
    ball.goto(x, ground_y)
    ball.color("grey", "white")
    ball.begin_fill()
    ball.pendown()
    ball.circle(ball_radius)
    ball.end_fill()
    ball.penup()

    # Update rotation angle based on rolling distance
    angle -= (360 * step) / (2 * math.pi * ball_radius)

    # Draw HP group centered just above ball center
    draw_HP_group(letters, x, y - 5, angle)

    # Calculate progress (0 to 1)
    progress = (x - start_x) / total_distance
    letters_to_show = int(progress * total_letters)

    # Show the substring of the farewell message aligned left at ground line start
    current_text = farewell_msg[:letters_to_show]
    text_turtle.goto(-300, -30)  # leftmost point of ground line
    text_turtle.write(current_text, align="left", font=("Arial", 17, "italic"))

    screen.update()
    time.sleep(0.01)  # Slightly slower frame delay for smooth effect

# Pause before enlargement
time.sleep(0.5)

# --- Enlargement animation after rolling finishes ---

final_x = end_x
final_y = y  # ball center y

max_radius = max(screen.window_width(), screen.window_height()) * 1.2  # big enough to cover entire screen

enlarge_steps = 60

for i in range(enlarge_steps):
    ball.clear()  # clear only previous big circle

    current_radius = ball_radius + (max_radius - ball_radius) * (i / enlarge_steps)

    ball.goto(final_x, final_y - current_radius)  # position at bottom of circle
    ball.color("white", "white")
    ball.begin_fill()
    ball.pendown()
    ball.circle(current_radius)
    ball.end_fill()
    ball.penup()

    screen.update()
    time.sleep(0.02)

# Show final message
final_msg_turtle = turtle.Turtle()
final_msg_turtle.hideturtle()
final_msg_turtle.penup()
final_msg_turtle.color("grey")

# First line
final_msg_turtle.goto(0, 10)
final_msg_turtle.write(
    "Even though the internship is already done, I hope we can still keep in contact in the future!",
    align="center",
    font=("Times New Roman", 14, "italic")
)

screen.update()
time.sleep(1.5)  # Wait 1 second before showing second line

# Second line appears after 1 second
final_msg_turtle.color("maroon")
final_msg_turtle.goto(0, -10)
final_msg_turtle.write(
    "(Let me know if your chili stocks are low HAHA)",
    align="center",
    font=("Times New Roman", 12, "italic")
)

screen.update()

turtle.done()
