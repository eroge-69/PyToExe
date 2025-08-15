import turtle as t
import sys
# Scores
player_a_score = 0
player_b_score = 0

# Screen setup
window = t.Screen()
window.title("The Pong Game")
window.bgcolor("green")
window.setup(width=800, height=600)
window.tracer(0)  # manual screen updates

# Left paddle
leftpaddle = t.Turtle()
leftpaddle.speed(0)
leftpaddle.shape("square")
leftpaddle.color("white")
leftpaddle.shapesize(stretch_wid=5, stretch_len=1)
leftpaddle.penup()
leftpaddle.goto(-350, 0)

# Right paddle
rightpaddle = t.Turtle()
rightpaddle.speed(0)
rightpaddle.shape("square")
rightpaddle.color("white")
rightpaddle.shapesize(stretch_wid=5, stretch_len=1)
rightpaddle.penup()
rightpaddle.goto(350, 0)

# Ball
ball = t.Turtle()
ball.speed(0)
ball.shape("circle")
ball.color("red")
ball.penup()
ball.goto(0, 0)
ball_dx = 0.2
ball_dy = 0.2

# Pen for score
pen = t.Turtle()
pen.speed(0)
pen.color("blue")
pen.penup()
pen.hideturtle()
pen.goto(0, 260)
pen.write("Player A: 0   Player B: 0", align="center", font=('Arial', 24, 'normal'))

# Paddle movement functions
def leftpaddle_up():
    y = leftpaddle.ycor()
    if y < 250:  # prevent going off screen
        y += 20
        leftpaddle.sety(y)

def leftpaddle_down():
    y = leftpaddle.ycor()
    if y > -250:
        y -= 20
        leftpaddle.sety(y)

def rightpaddle_up():
    y = rightpaddle.ycor()
    if y < 250:
        y += 20
        rightpaddle.sety(y)

def rightpaddle_down():
    y = rightpaddle.ycor()
    if y > -250:
        y -= 20
        rightpaddle.sety(y)

# Key bindings
window.listen()
window.onkeypress(leftpaddle_up, 'w')
window.onkeypress(leftpaddle_down, 's')
window.onkeypress(rightpaddle_up, 'Up')
window.onkeypress(rightpaddle_down, 'Down')

running= True
while running:
    window.update()

    # Move the ball
    ball.setx(ball.xcor() + ball_dx)
    ball.sety(ball.ycor() + ball_dy)

    # Top/bottom border collision
    if ball.ycor() > 290:
        ball.sety(290)
        ball_dy *= -1

    if ball.ycor() < -290:
        ball.sety(-290)
        ball_dy *= -1

    # Right wall (Player A scores)
    if ball.xcor() > 390:
        ball.goto(0, 0)
        ball_dx = 0.2  # reset speed
        ball_dy = 0.2
        ball_dx *= -1
        player_a_score += 1
        pen.clear()
        pen.write(f"Player A: {player_a_score}   Player B: {player_b_score}",
                  align="center", font=('Arial', 24, 'normal'))

    # Left wall (Player B scores)
    if ball.xcor() < -390:
        ball.goto(0, 0)
        ball_dx = 0.2  # reset speed
        ball_dy = 0.2
        ball_dx *= -1
        player_b_score += 1
        pen.clear()
        pen.write(f"Player A: {player_a_score}   Player B: {player_b_score}",
                  align="center", font=('Arial', 24, 'normal'))

    # Paddle collision (Right)
    if (340 < ball.xcor() < 350) and (rightpaddle.ycor() - 50 < ball.ycor() < rightpaddle.ycor() + 50):
        ball.setx(340)
        ball_dx *= -1.1  # reverse and speed up
        ball_dy *= 1.1

    # Paddle collision (Left)
    if (-350 < ball.xcor() < -340) and (leftpaddle.ycor() - 50 < ball.ycor() < leftpaddle.ycor() + 50):
        ball.setx(-340)
        ball_dx *= -1.1  # reverse and speed up
        ball_dy *= 1.1
    if player_a_score==15 :
        pen = t.Turtle()
        pen.speed(0)
        pen.color("blue")
        pen.penup()
        pen.hideturtle()
        pen.goto(20,60)
        pen.write("Player A Wins", align="center", font=('Arial',40,'normal'))
        running= False
    elif player_b_score==1:
        pen = t.Turtle()
        pen.speed(0)
        pen.color("blue")
        pen.penup()
        pen.hideturtle()
        pen.goto(20,60)
        pen.write("Player B Wins", align="center", font=('Arial',40,'normal'))
        running= False
    else:
        running=True
        
