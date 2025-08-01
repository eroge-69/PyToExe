import turtle

turtle.Screen().bgcolor("blue")

board = turtle.Turtle()

#star
board.forward(100)
board.left(120)
board.forward(100)
board.left(120)
board.forward(100)

board.penup()
board.right(150)
board.forward(50)

#2
board.pendown()
board.right(90)
board.forward(100)
board.right(120)
board.forward(100)
board.right(120)
board.forward(100)
turtle.delay(10000)