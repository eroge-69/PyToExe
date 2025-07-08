import turtle

# Set up the Turtle environment
turtle.speed(3)  # Control the drawing speed
turtle.bgcolor('black')  # Set the background color
turtle.pensize(3)  # Set the pen thickness

# Define the curved part of the heart
def func():
    for i in range(200):
        turtle.right(1)  # Rotate slightly
        turtle.forward(1)  # Move forward

# Set the pen and fill colors
turtle.color('red', 'pink')
turtle.begin_fill()

# Draw the heart shape
turtle.left(140)
turtle.forward(111.65)  # Draw the left diagonal line
func()  # Draw the left curve
turtle.left(120)
func()  # Draw the right curve
turtle.forward(111.65)  # Draw the right diagonal line

turtle.end_fill()  # Fill the heart with the color
turtle.hideturtle()  # Hide the turtle cursor
turtle.done()  # Finish the drawing